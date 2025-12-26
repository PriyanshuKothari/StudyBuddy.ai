import React, { useState } from 'react';
import { Upload, MessageSquare, BarChart3, BookOpen, Send, Trash2, FileText, CheckCircle, Loader2, AlertCircle, Copy, Check } from 'lucide-react';

// ============================================
// TYPE DEFINITIONS
// ============================================

interface UploadResponse {
  success: boolean;
  filename: string;
  file_id: string;
  num_chunks: number;
  vector_store_ready: boolean;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    chunk_id: number;
    content_preview: string;
    similarity: number;
  }>;
  timestamp: string;
}

interface ChatResponse {
  success: boolean;
  answer: string;
  sources: Array<{
    chunk_id: number;
    content_preview: string;
    similarity: number;
  }>;
  session_id: string;
  message_count: number;
}

interface TopicAnalysis {
  topic: string;
  frequency: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

interface MockQuestion {
  question_number: number;
  text: string;
  topic: string;
  difficulty: string;
}

// ============================================
// API CLIENT
// ============================================

const API_BASE_URL = 'https://priyanshukothari-studybuddy-ai.hf.space';

const api = {
  uploadPDF: async (file: File, type: 'syllabus' | 'pyq'): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const endpoint = type === 'syllabus' ? '/api/v1/upload/pdf' : '/api/v1/pyq/upload';
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) throw new Error('Upload failed');
    return response.json();
  },

  chat: async (fileId: string, question: string, sessionId: string): Promise<ChatResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/rag/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_id: fileId, question, session_id: sessionId }),
    });
    
    if (!response.ok) throw new Error('Chat request failed');
    return response.json();
  },

  analyzePYQ: async (syllabusId: string, pyqId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/pyq/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ syllabus_file_id: syllabusId, pyq_file_id: pyqId }),
    });
    
    if (!response.ok) throw new Error('Analysis failed');
    return response.json();
  },

  generateMockQuestions: async (syllabusId: string, topic: string, numQuestions: number) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/pyq/generate-mock`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ syllabus_file_id: syllabusId, topic, num_questions: numQuestions }),
    });
    
    if (!response.ok) throw new Error('Question generation failed');
    return response.json();
  },

  clearHistory: async (sessionId: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/rag/history/${sessionId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) throw new Error('Clear history failed');
    return response.json();
  },
};

// ============================================
// MAIN APP COMPONENT
// ============================================

export default function StudyBuddyApp() {
  const [currentPage, setCurrentPage] = useState<'upload' | 'chat' | 'analysis' | 'practice'>('upload');
  const [syllabusFile, setSyllabusFile] = useState<UploadResponse | null>(null);
  const [pyqFile, setPyqFile] = useState<UploadResponse | null>(null);
  const [sessionId] = useState(`session_${Date.now()}`);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-primary-600">StudyBuddy.ai</h1>
          <p className="text-sm text-gray-500 mt-1">AI Study Assistant</p>
        </div>

        <nav className="flex-1 p-4">
          <button
            onClick={() => setCurrentPage('upload')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
              currentPage === 'upload' ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'
            }`}
          >
            <Upload size={20} />
            <span className="font-medium">Upload Files</span>
          </button>

          <button
            onClick={() => setCurrentPage('chat')}
            disabled={!syllabusFile}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
              currentPage === 'chat' ? 'bg-primary-50 text-primary-700' : 
              syllabusFile ? 'hover:bg-gray-50 text-gray-700' : 'text-gray-400 cursor-not-allowed'
            }`}
          >
            <MessageSquare size={20} />
            <span className="font-medium">Chat</span>
          </button>

          <button
            onClick={() => setCurrentPage('analysis')}
            disabled={!syllabusFile || !pyqFile}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
              currentPage === 'analysis' ? 'bg-primary-50 text-primary-700' : 
              (syllabusFile && pyqFile) ? 'hover:bg-gray-50 text-gray-700' : 'text-gray-400 cursor-not-allowed'
            }`}
          >
            <BarChart3 size={20} />
            <span className="font-medium">PYQ Analysis</span>
          </button>

          <button
            onClick={() => setCurrentPage('practice')}
            disabled={!syllabusFile}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
              currentPage === 'practice' ? 'bg-primary-50 text-primary-700' : 
              syllabusFile ? 'hover:bg-gray-50 text-gray-700' : 'text-gray-400 cursor-not-allowed'
            }`}
          >
            <BookOpen size={20} />
            <span className="font-medium">Practice</span>
          </button>
        </nav>

        {syllabusFile && (
          <div className="p-4 border-t border-gray-200 bg-gray-50">
            <div className="text-xs text-gray-500 mb-1">Syllabus</div>
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <FileText size={16} className="text-primary-500" />
              <span className="truncate">{syllabusFile.filename}</span>
            </div>
            {pyqFile && (
              <>
                <div className="text-xs text-gray-500 mb-1 mt-3">PYQ</div>
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <FileText size={16} className="text-accent-500" />
                  <span className="truncate">{pyqFile.filename}</span>
                </div>
              </>
            )}
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {currentPage === 'upload' && (
          <UploadPage 
            syllabusFile={syllabusFile}
            pyqFile={pyqFile}
            onSyllabusUpload={setSyllabusFile}
            onPyqUpload={setPyqFile}
          />
        )}
        {currentPage === 'chat' && syllabusFile && (
          <ChatPage fileId={syllabusFile.file_id} sessionId={sessionId} />
        )}
        {currentPage === 'analysis' && syllabusFile && pyqFile && (
          <AnalysisPage syllabusId={syllabusFile.file_id} pyqId={pyqFile.file_id} />
        )}
        {currentPage === 'practice' && syllabusFile && (
          <PracticePage syllabusId={syllabusFile.file_id} />
        )}
      </main>
    </div>
  );
}

// ============================================
// UPLOAD PAGE
// ============================================

function UploadPage({ 
  syllabusFile, 
  pyqFile, 
  onSyllabusUpload, 
  onPyqUpload 
}: { 
  syllabusFile: UploadResponse | null;
  pyqFile: UploadResponse | null;
  onSyllabusUpload: (file: UploadResponse) => void;
  onPyqUpload: (file: UploadResponse) => void;
}) {
  return (
    <div className="max-w-4xl mx-auto p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-2">Upload Your Documents</h2>
      <p className="text-gray-600 mb-8">Upload your syllabus and previous year questions to get started</p>

      <div className="grid md:grid-cols-2 gap-6">
        <FileUploadCard
          title="Syllabus PDF"
          description="Upload your course syllabus to chat and generate practice questions"
          uploadedFile={syllabusFile}
          onUpload={onSyllabusUpload}
          type="syllabus"
          required
        />

        <FileUploadCard
          title="PYQ PDF (Optional)"
          description="Upload previous year questions to analyze topic frequency and patterns"
          uploadedFile={pyqFile}
          onUpload={onPyqUpload}
          type="pyq"
        />
      </div>

      {syllabusFile && (
        <div className="mt-8 p-6 bg-accent-50 rounded-lg border border-accent-200">
          <div className="flex items-start gap-3">
            <CheckCircle className="text-accent-600 mt-0.5" size={20} />
            <div>
              <h3 className="font-semibold text-accent-900 mb-1">Ready to Go!</h3>
              <p className="text-accent-700 text-sm">
                Your syllabus has been processed into {syllabusFile.num_chunks} chunks. 
                You can now chat with your study material or generate practice questions.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function FileUploadCard({ 
  title, 
  description, 
  uploadedFile, 
  onUpload, 
  type,
  required = false
}: {
  title: string;
  description: string;
  uploadedFile: UploadResponse | null;
  onUpload: (file: UploadResponse) => void;
  type: 'syllabus' | 'pyq';
  required?: boolean;
}) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await api.uploadPDF(file, type);
      onUpload(response);
    } catch (err) {
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-primary-400 transition-colors bg-white">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {title}
        {required && <span className="text-red-500 ml-1">*</span>}
      </h3>
      <p className="text-sm text-gray-600 mb-4">{description}</p>

      {!uploadedFile ? (
        <label className="block">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            disabled={uploading}
            className="hidden"
          />
          <div className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg cursor-pointer transition-colors ${
            uploading 
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
              : 'bg-primary-500 text-white hover:bg-primary-600'
          }`}>
            {uploading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Upload size={20} />
                <span>Choose PDF File</span>
              </>
            )}
          </div>
        </label>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
            <CheckCircle className="text-green-600" size={20} />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-green-900 truncate">
                {uploadedFile.filename}
              </div>
              <div className="text-xs text-green-700">
                {uploadedFile.num_chunks} chunks created
              </div>
            </div>
          </div>
          <label className="block">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={uploading}
              className="hidden"
            />
            <div className="text-center text-sm text-primary-600 hover:text-primary-700 cursor-pointer">
              Upload different file
            </div>
          </label>
        </div>
      )}

      {error && (
        <div className="mt-3 flex items-center gap-2 text-sm text-red-600">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

// ============================================
// CHAT PAGE
// ============================================

function ChatPage({ fileId, sessionId }: { fileId: string; sessionId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.chat(fileId, input, sessionId);
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      await api.clearHistory(sessionId);
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear history');
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-gray-200 bg-white px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Chat with Your Syllabus</h2>
          <p className="text-sm text-gray-500 mt-1">Ask questions about your study material</p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearHistory}
            className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <Trash2 size={16} />
            Clear History
          </button>
        )}
      </div>

      <div className="flex-1 overflow-auto p-6">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <MessageSquare size={48} className="mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Start a Conversation</h3>
              <p className="text-gray-500 max-w-sm">
                Ask questions about your syllabus, concepts, or topics you want to learn more about.
              </p>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <MessageBubble key={index} message={message} />
            ))}
            {loading && (
              <div className="flex items-center gap-3 text-gray-500">
                <Loader2 size={20} className="animate-spin" />
                <span>Thinking...</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 bg-white p-6">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a question about your syllabus..."
            disabled={loading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-50"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <Send size={20} />
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-primary-500 text-white px-6 py-3 rounded-2xl rounded-tr-sm max-w-2xl">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="bg-white border border-gray-200 px-6 py-4 rounded-2xl rounded-tl-sm max-w-2xl shadow-sm">
        <div className="prose prose-sm max-w-none whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
      
      {message.sources && message.sources.length > 0 && (
        <div className="ml-4 space-y-2">
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">Sources</div>
          {message.sources.map((source, idx) => (
            <div key={idx} className="bg-gray-50 border border-gray-200 px-4 py-2 rounded-lg text-sm">
              <div className="text-gray-700 line-clamp-2">{source.content_preview}</div>
              <div className="text-xs text-gray-500 mt-1">
                Relevance: {(source.similarity * 100).toFixed(0)}%
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================
// ANALYSIS PAGE
// ============================================

function AnalysisPage({ syllabusId, pyqId }: { syllabusId: string; pyqId: string }) {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const result = await api.analyzePYQ(syllabusId, pyqId);
      setAnalysis(result);
    } catch (error) {
      console.error('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-2">PYQ Analysis</h2>
      <p className="text-gray-600 mb-8">Analyze previous year questions to identify important topics</p>

      {!analysis ? (
        <div className="text-center py-12">
          <BarChart3 size={48} className="mx-auto text-gray-300 mb-4" />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-gray-300 transition-colors inline-flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <BarChart3 size={20} />
                Start Analysis
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Topic Frequency</h3>
            <div className="space-y-3">
              {analysis.topic_frequency?.map((item: TopicAnalysis, idx: number) => (
                <div key={idx} className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">{item.topic}</span>
                      <span className="text-sm text-gray-500">{item.frequency} questions</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${
                          item.priority === 'HIGH' ? 'bg-red-500' : 
                          item.priority === 'MEDIUM' ? 'bg-yellow-500' : 
                          'bg-green-500'
                        }`}
                        style={{ width: `${(item.frequency / Math.max(...analysis.topic_frequency.map((t: TopicAnalysis) => t.frequency))) * 100}%` }}
                      />
                    </div>
                  </div>
                  <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                    item.priority === 'HIGH' ? 'bg-red-100 text-red-700' : 
                    item.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' : 
                    'bg-green-100 text-green-700'
                  }`}>
                    {item.priority}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {analysis.recommendations && (
            <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">Recommendations</h3>
              <ul className="space-y-2">
                {analysis.recommendations.map((rec: string, idx: number) => (
                  <li key={idx} className="text-sm text-blue-800 flex items-start gap-2">
                    <span className="text-blue-500 mt-0.5">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================
// PRACTICE PAGE
// ============================================

function PracticePage({ syllabusId }: { syllabusId: string }) {
  const [topic, setTopic] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [questions, setQuestions] = useState<MockQuestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    if (!topic.trim()) return;

    setLoading(true);
    try {
      const result = await api.generateMockQuestions(syllabusId, topic, numQuestions);
      setQuestions(result.questions || []);
    } catch (error) {
      console.error('Question generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    const text = questions.map(q => `${q.question_number}. ${q.text}\n`).join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-2">Practice Questions</h2>
      <p className="text-gray-600 mb-8">Generate custom practice questions from your syllabus</p>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Topic
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Linear Regression, Decision Trees"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Questions: {numQuestions}
            </label>
            <input
              type="range"
              min="1"
              max="20"
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
              className="w-full"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={!topic.trim() || loading}
            className="w-full px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-gray-300 transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Generating Questions...
              </>
            ) : (
              <>
                <BookOpen size={20} />
                Generate Questions
              </>
            )}
          </button>
        </div>
      </div>

      {questions.length > 0 && (
        <>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900">
              Generated Questions ({questions.length})
            </h3>
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              {copied ? (
                <>
                  <Check size={16} className="text-green-600" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy size={16} />
                  Copy All
                </>
              )}
            </button>
          </div>

          <div className="space-y-4">
            {questions.map((q) => (
              <div key={q.question_number} className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-semibold text-primary-700">
                      {q.question_number}
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-900 mb-3">{q.text}</p>
                    <div className="flex items-center gap-3 text-sm">
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded">
                        {q.topic}
                      </span>
                      <span className={`px-2 py-1 rounded ${
                        q.difficulty === 'hard' ? 'bg-red-100 text-red-700' :
                        q.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {q.difficulty}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}