import React, { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { Send, MessageSquare, X } from 'lucide-react';

interface ChatInputProps {
  onPromptSubmit: (prompt: string) => void;
  disabled: boolean;
  initialPrompt?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({ onPromptSubmit, disabled, initialPrompt = '' }) => {
  const [prompt, setPrompt] = useState(initialPrompt);

  useEffect(() => {
    setPrompt(initialPrompt);
  }, [initialPrompt]);

  const examplePrompts = [
    "show me something in red",
    "more formal options",
    "casual summer wear",
    "matching accessories",
  ];

  const handleExampleClick = (example: string) => {
    setPrompt(example);
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (prompt.trim()) {
      onPromptSubmit(prompt.trim());
    }
  };

  const clearPrompt = () => {
    setPrompt('');
  };

  return (
    <div className="chat-input-area section">
      <h2><MessageSquare size={24} />Refine with a Prompt</h2>
      <form onSubmit={handleSubmit}>
        <div className="prompt-input-wrapper">
          <input
            type="text"
            className="prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., 'dark blue jeans', 'elegant dress'"
            disabled={disabled}
            aria-label="Enter prompt to refine search"
          />
          {prompt && (
            <button 
              type="button" 
              onClick={clearPrompt} 
              className="prompt-clear-btn" /* Only its specific class now */
              aria-label="Clear prompt"
              title="Clear prompt"
            >
              <X size={18}/>
            </button>
          )}
        </div>
        <button type="submit" disabled={disabled || !prompt.trim()}>
          <Send size={20}/> Send
        </button>
      </form>
      <div className="prompt-examples">
        <strong>Try:</strong>
        <ul>
          {examplePrompts.map((ex, idx) => (
            <li key={idx} onClick={() => handleExampleClick(ex)} role="button" tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && handleExampleClick(ex)}>
              {ex}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
export default ChatInput;
