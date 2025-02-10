from flask import Flask, render_template, request, jsonify
import ollama
import PyPDF2

app = Flask(__name__)

def read_pdf(file_storage):
    """Reads a PDF file from a FileStorage object and extracts text."""
    text = ""
    reader = PyPDF2.PdfReader(file_storage)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

@app.route('/')
def index():
    return render_template('chatbot_interface.html')

# Initialize conversation history
conversation_history = []
pdf_content = ""

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history, pdf_content
    user_input = request.form['user_input']
    pdf_file = request.files.get('pdf_content')

    if pdf_file:
        # Read the PDF content if a file is uploaded
        pdf_content = read_pdf(pdf_file)
        conversation_history.append({'role': 'user', 'content': pdf_content})
        return jsonify({'response': 'PDF content loaded. You can now ask questions about it.'})

    # Append the new user input to the conversation history
    conversation_history.append({'role': 'user', 'content': user_input})

    print(f"User input: {user_input}")  # Debug statement

    # Limit the conversation history based on token count
    while len(conversation_history) > 0:
        # Check the total token count (this is a placeholder for actual token counting logic)
        total_tokens = sum(len(msg['content'].split()) for msg in conversation_history)
        if total_tokens <= 2048:  # Adjust this limit based on the model's requirements
            break
        conversation_history.pop(0)  # Remove the oldest message

    try:
        # Send the entire conversation history to the model, including PDF content if available
        response = ollama.chat(model='llama3.1', messages=conversation_history)
        print(f"Response from Ollama: {response}")  # Debug statement
        
        if 'message' in response:
            # Append the chatbot's response to the conversation history
            conversation_history.append({'role': 'assistant', 'content': response['message']['content']})
            return jsonify({'response': response['message']['content']})
        else:
            return jsonify({'error': 'No response from the model.'})
    except Exception as e:
        print(f"Error: {e}")  # Debug statement
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
