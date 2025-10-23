from flask import Flask, render_template_string, request, jsonify
from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("⚠️ GROQ_API_KEY not found! Please set it in your .env file")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.7
)

linkedin_writer = Agent(
    role='LinkedIn Content Strategist',
    goal='Create engaging, professional LinkedIn posts that drive engagement',
    backstory="""You are an expert LinkedIn content creator with years of 
    experience crafting viral posts. You understand what makes content 
    engaging: storytelling, hooks, personal insights, and clear value 
    propositions. You write in a conversational yet professional tone.""",
    llm=llm,
    verbose=False
)

editor = Agent(
    role='Content Editor',
    goal='Polish and optimize the content for maximum LinkedIn engagement',
    backstory="""You are a meticulous editor who ensures every post is 
    clear, impactful, and follows LinkedIn best practices. You add 
    relevant hashtags, ensure proper formatting, and make the content 
    scannable and engaging.""",
    llm=llm,
    verbose=False
)


def create_linkedin_post(topic):
    writing_task = Task(
        description=f"""Create an engaging LinkedIn post about: {topic}

        Requirements:
        - Start with a strong hook that grabs attention
        - Share a personal insight or story if relevant
        - Provide 3-4 key takeaways or actionable tips
        - Keep it between 150-200 words
        - Use short paragraphs for readability
        - End with a question to encourage engagement
        - Write in a conversational, authentic tone""",
        agent=linkedin_writer,
        expected_output="A compelling LinkedIn post draft with all required elements"
    )

    editing_task = Task(
        description="""Review and optimize the LinkedIn post:

        - Ensure the hook is attention-grabbing
        - Add line breaks for better readability
        - Add 3-5 relevant hashtags at the end
        - Ensure it's engaging and professional
        - Make sure the call-to-action question is clear
        - Format it ready to copy-paste into LinkedIn""",
        agent=editor,
        expected_output="A polished, formatted LinkedIn post ready to publish"
    )

    crew = Crew(
        agents=[linkedin_writer, editor],
        tasks=[writing_task, editing_task],
        verbose=False
    )

    result = crew.kickoff()
    return str(result)


HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Post Generator ✨</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 900px;
            width: 100%;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .content {
            padding: 40px;
        }

        .input-section {
            margin-bottom: 30px;
        }

        label {
            display: block;
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 10px;
            color: #333;
        }

        .topic-input {
            width: 100%;
            padding: 15px 20px;
            font-size: 1rem;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            transition: all 0.3s ease;
        }

        .topic-input:focus {
            outline: none;
            border-color: #0077b5;
            box-shadow: 0 0 0 3px rgba(0, 119, 181, 0.1);
        }

        .examples {
            margin-top: 15px;
        }

        .examples p {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 10px;
        }

        .example-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .chip {
            background: #f0f0f0;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }

        .chip:hover {
            background: #0077b5;
            color: white;
            transform: translateY(-2px);
        }

        .generate-btn {
            width: 100%;
            padding: 18px;
            font-size: 1.1rem;
            font-weight: 600;
            background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%);
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .generate-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 119, 181, 0.3);
        }

        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 12px;
            font-weight: 500;
            text-align: center;
            display: none;
        }

        .status.active {
            display: block;
        }

        .status.writing {
            background: #fff3cd;
            color: #856404;
            border: 2px solid #ffc107;
        }

        .status.editing {
            background: #d1ecf1;
            color: #0c5460;
            border: 2px solid #17a2b8;
        }

        .status.complete {
            background: #d4edda;
            color: #155724;
            border: 2px solid #28a745;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #dc3545;
        }

        .result-section {
            margin-top: 30px;
            display: none;
        }

        .result-section.show {
            display: block;
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .result-header h2 {
            color: #333;
            font-size: 1.5rem;
        }

        .copy-btn {
            padding: 10px 20px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }

        .copy-btn:hover {
            background: #218838;
            transform: scale(1.05);
        }

        .copy-btn.copied {
            background: #0077b5;
        }

        .post-preview {
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 25px;
            white-space: pre-wrap;
            font-size: 1rem;
            line-height: 1.7;
            color: #333;
            max-height: 500px;
            overflow-y: auto;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }

        .stat-card .number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-card .label {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }

            .stats {
                grid-template-columns: 1fr;
            }

            .content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <svg width="40" height="40" viewBox="0 0 24 24" fill="white">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
                LinkedIn Post Generator
            </h1>
            <p>✨ Create engaging LinkedIn posts powered by AI in seconds</p>
        </div>

        <div class="content">
            <div class="input-section">
                <label for="topic">What do you want to write about?</label>
                <input 
                    type="text" 
                    id="topic" 
                    class="topic-input" 
                    placeholder="e.g., AI in healthcare, Remote work productivity, Leadership lessons..."
                    autocomplete="off"
                >

                <div class="examples">
                    <p>💡 Try these popular topics:</p>
                    <div class="example-chips">
                        <span class="chip">AI in healthcare</span>
                        <span class="chip">Remote work productivity</span>
                        <span class="chip">Leadership lessons</span>
                        <span class="chip">Career growth tips</span>
                        <span class="chip">Digital transformation</span>
                    </div>
                </div>
            </div>

            <button class="generate-btn" id="generateBtn">
                <span id="btnText">🚀 Generate LinkedIn Post</span>
                <div class="spinner" id="spinner" style="display: none;"></div>
            </button>

            <div class="status" id="status"></div>

            <div class="result-section" id="resultSection">
                <div class="result-header">
                    <h2>📝 Your LinkedIn Post</h2>
                    <button class="copy-btn" id="copyBtn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        <span id="copyText">Copy Post</span>
                    </button>
                </div>
                <div class="post-preview" id="postPreview"></div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="number" id="wordCount">0</div>
                        <div class="label">Words</div>
                    </div>
                    <div class="stat-card">
                        <div class="number" id="hashtagCount">0</div>
                        <div class="label">Hashtags</div>
                    </div>
                    <div class="stat-card">
                        <div class="number" id="lineCount">0</div>
                        <div class="label">Lines</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            Powered by CrewAI & Groq | Made with ❤️ for LinkedIn Creators
        </div>
    </div>

    <script>
        // Topic chip selection
        document.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', function() {
                document.getElementById('topic').value = this.textContent;
                document.querySelectorAll('.chip').forEach(c => c.style.background = '#f0f0f0');
                this.style.background = '#0077b5';
                this.style.color = 'white';
            });
        });

        // Generate post function
        document.getElementById('generateBtn').addEventListener('click', async function() {
            const topic = document.getElementById('topic').value.trim();

            if (!topic) {
                showStatus('error', '⚠️ Please enter a topic to create magic!');
                return;
            }

            const btn = document.getElementById('generateBtn');
            const btnText = document.getElementById('btnText');
            const spinner = document.getElementById('spinner');
            const resultSection = document.getElementById('resultSection');

            btn.disabled = true;
            btnText.textContent = 'Generating...';
            spinner.style.display = 'block';
            resultSection.classList.remove('show');

            showStatus('writing', '✍️ AI Writer is crafting your post...');

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ topic: topic })
                });

                const data = await response.json();

                if (data.success) {
                    showStatus('editing', '✨ Editor is polishing and optimizing...');

                    setTimeout(() => {
                        showStatus('complete', '✅ Your post is ready!');

                        const postPreview = document.getElementById('postPreview');
                        postPreview.textContent = data.post;

                        const wordCount = data.post.split(/\s+/).filter(w => w.length > 0).length;
                        const hashtagCount = (data.post.match(/#/g) || []).length;
                        const lineCount = data.post.split('\n').filter(line => line.trim()).length;

                        document.getElementById('wordCount').textContent = wordCount;
                        document.getElementById('hashtagCount').textContent = hashtagCount;
                        document.getElementById('lineCount').textContent = lineCount;

                        resultSection.classList.add('show');

                        setTimeout(() => {
                            document.getElementById('status').style.display = 'none';
                        }, 3000);
                    }, 1500);
                } else {
                    showStatus('error', '❌ Error: ' + data.error);
                }
            } catch (error) {
                showStatus('error', '❌ Error generating post. Please check your connection and try again.');
                console.error('Error:', error);
            } finally {
                btn.disabled = false;
                btnText.textContent = '🚀 Generate LinkedIn Post';
                spinner.style.display = 'none';
            }
        });

        // Copy post function
        document.getElementById('copyBtn').addEventListener('click', function() {
            const postText = document.getElementById('postPreview').textContent;
            const copyBtn = document.getElementById('copyBtn');
            const copyText = document.getElementById('copyText');

            navigator.clipboard.writeText(postText).then(() => {
                copyBtn.classList.add('copied');
                copyText.textContent = 'Copied! ✓';

                setTimeout(() => {
                    copyBtn.classList.remove('copied');
                    copyText.textContent = 'Copy Post';
                }, 2000);
            }).catch(err => {
                alert('Failed to copy. Please select and copy manually.');
            });
        });

        function showStatus(type, message) {
            const status = document.getElementById('status');
            status.className = 'status active ' + type;
            status.textContent = message;
        }

        document.getElementById('topic').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                document.getElementById('generateBtn').click();
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        topic = data.get('topic', '')

        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'})

        print(f"\n🔄 Generating post for topic: {topic}")
        post = create_linkedin_post(topic)
        print(f"✅ Post generated successfully!")

        return jsonify({'success': True, 'post': post})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 LinkedIn Post Generator Web App")
    print("=" * 70)
    print("\n✨ Starting server...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 70)

    app.run(debug=True, host='0.0.0.0', port=5000)