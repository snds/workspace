import { useEffect, useRef, useState } from "react";
import { nanoid } from "nanoid";
import { Bot, User, Send, RefreshCw, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useOnboardingStore } from "@/stores/onboarding.store";
import { streamFrameworkAdvice, parseRecommendation } from "@/lib/ai/client";
import { WizardNavButtons } from "../components/WizardNavButtons";
import type { TechStackRecommendation } from "@/types/onboarding";

// ── Chat bubble ────────────────────────────────────────────────────────────

function ChatBubble({
  role,
  content,
  isStreaming,
}: {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}) {
  const isUser = role === "user";

  // Don't render the hidden __INIT__ trigger message
  if (content === "__INIT__") return null;

  // Strip recommendation code blocks from displayed content
  const displayContent = content
    .replace(/```recommendation[\s\S]*?```/, "")
    .trim();

  if (!displayContent && !isStreaming) return null;

  return (
    <div
      className={cn(
        "flex gap-2.5",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      <div
        className={cn(
          "w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5",
          isUser
            ? "bg-[var(--mauve-5)]"
            : "bg-[var(--violet-9)]"
        )}
      >
        {isUser ? (
          <User className="w-3 h-3 text-[var(--mauve-11)]" />
        ) : (
          <Bot className="w-3 h-3 text-white" />
        )}
      </div>
      <div
        className={cn(
          "max-w-[80%] rounded-xl px-3.5 py-2.5 text-xs leading-relaxed",
          isUser
            ? "bg-[var(--mauve-4)] text-[var(--mauve-12)] rounded-tr-sm"
            : "bg-[var(--mauve-3)] border border-[var(--mauve-5)] text-[var(--mauve-12)] rounded-tl-sm"
        )}
      >
        {displayContent || (
          <span className="text-[var(--mauve-9)]">Thinking…</span>
        )}
        {isStreaming && (
          <span className="inline-block w-1 h-3 bg-[var(--violet-9)] ml-0.5 animate-pulse rounded-sm" />
        )}
      </div>
    </div>
  );
}

// ── Recommendation card ────────────────────────────────────────────────────

function RecommendationCard({
  rec,
  onConfirm,
  onReset,
}: {
  rec: TechStackRecommendation;
  onConfirm: () => void;
  onReset: () => void;
}) {
  const fields: { label: string; value: string }[] = [
    { label: "Framework", value: rec.framework },
    { label: "Styling", value: rec.cssApproach },
    { label: "Components", value: rec.componentLibrary },
    { label: "Tokens", value: rec.tokenFormat },
  ];

  return (
    <div className="border border-[var(--violet-6)] bg-[var(--violet-2)] rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-2">
        <div className="w-5 h-5 rounded-full bg-[var(--violet-9)] flex items-center justify-center">
          <Bot className="w-3 h-3 text-white" />
        </div>
        <p className="text-xs font-semibold text-[var(--violet-12)]">
          Recommendation
        </p>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {fields.map(({ label, value }) => (
          <div key={label} className="bg-[var(--violet-3)] rounded-lg px-3 py-2">
            <p className="text-[10px] text-[var(--violet-10)] mb-0.5">{label}</p>
            <p className="text-xs font-medium text-[var(--violet-12)]">{value}</p>
          </div>
        ))}
      </div>

      {rec.rationale && (
        <p className="text-[10px] text-[var(--violet-11)] leading-relaxed border-t border-[var(--violet-5)] pt-2">
          {rec.rationale}
        </p>
      )}

      <div className="flex gap-2 pt-1">
        <Button
          size="sm"
          onClick={onConfirm}
          disabled={rec.confirmed}
          className="flex-1 gap-1.5 bg-[var(--violet-9)] hover:bg-[var(--violet-10)] text-white border-0"
        >
          <Check className="w-3 h-3" />
          {rec.confirmed ? "Confirmed" : "Looks good"}
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={onReset}
          className="gap-1.5 border-[var(--violet-6)] text-[var(--violet-11)] hover:bg-[var(--violet-3)]"
        >
          <RefreshCw className="w-3 h-3" />
          Reconsider
        </Button>
      </div>
    </div>
  );
}

// ── Step ───────────────────────────────────────────────────────────────────

export function FrameworkStep() {
  const {
    chatHistory,
    isAiStreaming,
    recommendation,
    appendChatMessage,
    updateLastAssistantMessage,
    setAiStreaming,
    setRecommendation,
    confirmRecommendation,
    resetChat,
    nextStep,
    markStepComplete,
  } = useOnboardingStore();

  const [inputValue, setInputValue] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const initialized = useRef(false);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory.length, isAiStreaming]);

  // Kick off the conversation when step mounts
  useEffect(() => {
    if (initialized.current || chatHistory.length > 0) return;
    initialized.current = true;
    sendMessage("__INIT__");
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function sendMessage(userText: string) {
    if (isAiStreaming) return;

    // Add user message (hidden if it's the init trigger)
    const userMsg = { id: nanoid(), role: "user" as const, content: userText };
    appendChatMessage(userMsg);

    // Create empty streaming assistant message
    const assistantId = nanoid();
    appendChatMessage({
      id: assistantId,
      role: "assistant",
      content: "",
      isStreaming: true,
    });
    setAiStreaming(true);

    let fullContent = "";
    try {
      await streamFrameworkAdvice(
        [...chatHistory, userMsg].map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
        })),
        (delta) => {
          fullContent += delta;
          updateLastAssistantMessage(delta);
        }
      );

      // Check for recommendation
      const rec = parseRecommendation(fullContent);
      if (rec) setRecommendation(rec);
    } finally {
      setAiStreaming(false);
    }
  }

  const handleSend = () => {
    const text = inputValue.trim();
    if (!text || isAiStreaming) return;
    setInputValue("");
    sendMessage(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleConfirm = () => {
    confirmRecommendation();
    markStepComplete(2);
    nextStep();
  };

  const handleReset = () => {
    resetChat();
    initialized.current = false;
  };

  const canContinue =
    recommendation?.confirmed === true ||
    (recommendation !== null && chatHistory.length > 0);

  return (
    <div className="flex flex-col h-[520px]">
      {/* Header */}
      <div className="px-6 pt-6 pb-4 border-b border-[var(--mauve-4)] flex-shrink-0">
        <div className="flex items-center gap-2 mb-1">
          <Badge
            variant="outline"
            className="text-[10px] border-[var(--violet-7)] text-[var(--violet-11)] bg-[var(--violet-2)]"
          >
            AI Advisor
          </Badge>
        </div>
        <h2 className="text-lg font-bold text-[var(--mauve-12)]">
          Tech stack for your design system
        </h2>
        <p className="text-xs text-[var(--mauve-10)] mt-1">
          Answer a few questions and we'll recommend the right tools for your team.
        </p>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="px-6 py-4 flex flex-col gap-3">
            {chatHistory.map((msg, i) => (
              <ChatBubble
                key={msg.id}
                role={msg.role}
                content={msg.content}
                isStreaming={
                  msg.isStreaming && i === chatHistory.length - 1
                }
              />
            ))}

            {/* Recommendation card */}
            {recommendation && (
              <RecommendationCard
                rec={recommendation}
                onConfirm={handleConfirm}
                onReset={handleReset}
              />
            )}

            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      </div>

      {/* Input */}
      {!recommendation && (
        <div className="px-6 pb-4 flex-shrink-0 border-t border-[var(--mauve-4)] pt-3">
          <div className="flex gap-2 items-end">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Tell me about your tech stack…"
              rows={2}
              disabled={isAiStreaming}
              className="flex-1 resize-none bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded-lg px-3 py-2 text-xs text-[var(--mauve-12)] placeholder:text-[var(--mauve-8)] focus:outline-none focus:border-[var(--violet-7)] transition-colors disabled:opacity-50"
            />
            <Button
              size="icon"
              onClick={handleSend}
              disabled={!inputValue.trim() || isAiStreaming}
              className="w-8 h-8 bg-[var(--violet-9)] hover:bg-[var(--violet-10)] border-0 flex-shrink-0 disabled:opacity-40"
            >
              <Send className="w-3.5 h-3.5 text-white" />
            </Button>
          </div>
        </div>
      )}

      {/* Footer nav */}
      <div className="px-6 pb-6 flex-shrink-0">
        <WizardNavButtons
          canContinue={canContinue}
          onContinue={handleConfirm}
          showSkip
          continueLabel="Use this stack"
        />
      </div>
    </div>
  );
}
