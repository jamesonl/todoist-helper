import React, { useState } from "react";

interface ChatStep {
  agent: string;
  prompt: {
    system: string;
    user: string;
  };
}

interface ChatInterfaceProps {
  onSubmit?: (input: string) => Promise<ChatStep[]>;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ onSubmit }) => {
  const [input, setInput] = useState("");
  const [steps, setSteps] = useState<ChatStep[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!input.trim() || !onSubmit) return;
    setIsLoading(true);
    try {
      const result = await onSubmit(input);
      setSteps(result);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="chat-interface">
      <form onSubmit={handleSubmit} className="chat-interface__form">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Describe what you need help with..."
          rows={4}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Thinking..." : "Send"}
        </button>
      </form>
      <ol className="chat-interface__steps">
        {steps.map((step, index) => (
          <li key={`${step.agent}-${index}`}>
            <strong>{step.agent}</strong>
            <pre>{step.prompt.system}</pre>
            <pre>{step.prompt.user}</pre>
          </li>
        ))}
      </ol>
    </div>
  );
};

export default ChatInterface;
