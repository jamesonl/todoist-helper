import type { ChatInterfaceProps } from "../components/ChatInterface";

interface ChatResponse {
  steps: {
    agent: string;
    prompt: {
      system: string;
      user: string;
    };
  }[];
}

export async function submitChatRequest(
  input: string,
  context: Record<string, string> = {}
): Promise<ReturnType<NonNullable<ChatInterfaceProps["onSubmit"]>>> {
  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_request: input, context }),
  });
  if (!response.ok) {
    throw new Error(`Failed to submit chat request: ${response.status}`);
  }
  const json: ChatResponse = await response.json();
  return json.steps;
}
