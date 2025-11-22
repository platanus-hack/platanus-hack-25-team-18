import { useState, useRef, useEffect } from "react";
import { ChatBubble } from "@/components/molecules/ChatBubble";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}

interface ChatContainerProps {
  candidateName: string;
  onReveal: () => void;
  onBack: () => void;
  className?: string;
}

export const ChatContainer = ({
  candidateName,
  onReveal,
  onBack,
  className,
}: ChatContainerProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "¡Hola! Parece que tenemos muchas ideas en común. Pregúntame lo que quieras antes de revelar quién soy.",
      isUser: false,
      timestamp: "Ahora",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      isUser: true,
      timestamp: "Ahora",
    };

    setMessages((prev) => [...prev, userMessage]);

    // Simulate candidate response
    setTimeout(() => {
      const responses = [
        "Creo firmemente en esa postura. Es fundamental para el desarrollo del país.",
        "Ese es un tema complejo, pero mi compromiso es trabajar por una solución justa.",
        "Me alegra que compartas esa visión. Juntos podemos lograr grandes cambios.",
        "Es una de mis prioridades principales. Tengo un plan concreto para abordarlo.",
      ];

      const candidateMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: responses[Math.floor(Math.random() * responses.length)],
        isUser: false,
        timestamp: "Ahora",
      };

      setMessages((prev) => [...prev, candidateMessage]);
    }, 1000);

    setInputValue("");
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 ">
        {messages.map((message) => (
          <ChatBubble
            key={message.id}
            message={message.text}
            isUser={message.isUser}
            timestamp={message.timestamp}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Action buttons */}
      <div className="px-4 py-4 mt-44 border-t border-border/50 space-y-3 ">
        <Button
          onClick={onReveal}
          className="w-full gradient-primary text-primary-foreground font-semibold"
          size="lg"
        >
          Revelar Match
        </Button>
        <Button
          onClick={onBack}
          variant="outline"
          className="w-full"
          size="lg"
        >
          No me convence, seguir deslizando
        </Button>
      </div>

      {/* Input area */}
      <div className="px-4 py-6 mt-44 border-t border-border/50 bg-card/80 backdrop-blur-lg">
        <div className="flex gap-2">
          <Input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder="Pregúntale lo que quieras..."
            className="flex-1"
            autoComplete="off"
          />
          <Button
            onClick={handleSend}
            size="icon"
            className="gradient-primary text-primary-foreground"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};
