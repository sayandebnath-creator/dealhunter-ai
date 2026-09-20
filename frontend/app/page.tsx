"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { Fraunces, Inter } from "next/font/google";
import {
  ArrowUp,
  Target,
  ShieldCheck,
  ListTree,
  SlidersHorizontal,
  AlertTriangle,
} from "lucide-react";
import ReactMarkdown from "react-markdown";

const fraunces = Fraunces({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-fraunces",
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-inter",
});

type Message = {
  role: "user" | "assistant";
  content: string;
  isError?: boolean;
};

const starters = [
  { label: "Laptop under ₹70,000 for programming", hint: "budget · laptops" },
  { label: "Best phone under ₹30,000", hint: "budget · phones" },
  { label: "Laptop with great battery life", hint: "priority · laptops" },
];

const steps = [
  {
    icon: SlidersHorizontal,
    title: "Say what you need",
    description:
      "Budget, use case, deal-breakers — plain language is enough. No filters to configure.",
  },
  {
    icon: ListTree,
    title: "It compares the field",
    description:
      "DealHunter checks specs and current prices across listings rather than guessing from memory.",
  },
  {
    icon: ShieldCheck,
    title: "You get a shortlist, not a maze",
    description:
      "A few options with the trade-offs spelled out, so the choice is yours to make quickly.",
  },
];

export default function Home() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi, I'm DealHunter. Tell me what you're shopping for — your budget and what matters most — and I'll shortlist a few options that actually fit.",
    },
  ]);

  const scrollAnchorRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  async function sendMessage(message?: string) {
    const text = (message ?? input).trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) throw new Error("Failed to get response");

      const data = await response.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          isError: true,
          content:
            "I couldn't reach the DealHunter backend. Check that the FastAPI server is running on port 8000, then try again.",
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    sendMessage();
  }

  return (
    <main
      className={`${fraunces.variable} ${inter.variable} min-h-screen bg-[#F5F5F1] text-[#1C1D1B]`}
      style={{ fontFamily: "var(--font-inter)" }}
    >
      {/* Quiet background texture: a sparse grid, evoking a scan rather than decoration */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 opacity-[0.35]"
        style={{
          backgroundImage:
            "radial-gradient(circle, #C9C6BC 1px, transparent 1px)",
          backgroundSize: "28px 28px",
          maskImage:
            "linear-gradient(to bottom, black, black 30%, transparent 85%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, black, black 30%, transparent 85%)",
        }}
      />

      <div className="relative mx-auto flex min-h-screen max-w-5xl flex-col px-4 sm:px-8">
        {/* Header */}
        <header className="flex h-20 items-center justify-between border-b border-[#E1DFD5]">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-[#1C1D1B] text-[#F5F5F1]">
              <Target size={17} strokeWidth={1.75} />
            </div>
            <div>
              <p
                className="text-[15px] font-medium leading-none tracking-tight"
                style={{ fontFamily: "var(--font-fraunces)" }}
              >
                DealHunter
              </p>
              <p className="mt-1 text-[11px] leading-none text-[#82806F]">
                Shopping research assistant
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-[#5C6B60]">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#5C8A73] opacity-60 motion-reduce:animate-none" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-[#5C8A73]" />
            </span>
            Tracking live prices
          </div>
        </header>

        {/* Hero */}
        <section className="grid gap-10 pb-4 pt-14 sm:pt-20 md:grid-cols-[1.1fr_0.9fr] md:gap-16">
          <div>
            <h1
              className="text-[2.6rem] leading-[1.08] tracking-tight sm:text-[3.4rem]"
              style={{ fontFamily: "var(--font-fraunces)" }}
            >
              Stop comparing tabs.
              <br />
              <span className="italic text-[#9A5B2E]">Start with a question.</span>
            </h1>
            <p className="mt-6 max-w-md text-[15px] leading-7 text-[#5C5B54]">
              Most product search makes you do the comparing. DealHunter reads
              specs and prices for you, then explains the trade-offs in plain
              terms — so you spend less time deciding and more time using
              whatever you bought.
            </p>
          </div>

          <div className="flex flex-col justify-end gap-3 border-t border-[#E1DFD5] pt-6 md:border-t-0 md:border-l md:pl-10 md:pt-0">
            {steps.map(({ icon: Icon, title, description }) => (
              <div key={title} className="flex gap-3">
                <Icon size={16} strokeWidth={1.75} className="mt-1 shrink-0 text-[#9A5B2E]" />
                <div>
                  <p className="text-[13px] font-medium text-[#1C1D1B]">{title}</p>
                  <p className="mt-0.5 text-[13px] leading-5 text-[#82806F]">
                    {description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Chat */}
        <section className="pb-16">
          <div className="overflow-hidden rounded-2xl border border-[#E1DFD5] bg-[#FDFDFB] shadow-[0_1px_2px_rgba(28,29,27,0.04),0_12px_32px_-16px_rgba(28,29,27,0.12)]">
            <div
              role="log"
              aria-live="polite"
              aria-relevant="additions"
              className="max-h-[440px] min-h-[280px] space-y-5 overflow-y-auto p-5 sm:p-7"
            >
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === "user" ? "flex-row-reverse" : ""
                  }`}
                >
                  {message.role === "assistant" && (
                    <div
                      className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md ${
                        message.isError
                          ? "bg-[#F4E3DB] text-[#9A4A2E]"
                          : "bg-[#1C1D1B] text-[#F5F5F1]"
                      }`}
                    >
                      {message.isError ? (
                        <AlertTriangle size={14} strokeWidth={2} />
                      ) : (
                        <Target size={14} strokeWidth={1.75} />
                      )}
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-xl px-4 py-3 text-[14px] leading-6 ${
                      message.role === "user"
                        ? "bg-[#1C1D1B] text-[#F5F5F1]"
                        : message.isError
                        ? "border border-[#EAD3C6] bg-[#FBF3EE] text-[#7A3A22]"
                        : "border border-[#E1DFD5] bg-white text-[#2B2A26]"
                    }`}
                  >
                    {message.role === "assistant" ? (
                      <div className="prose prose-sm max-w-none prose-p:my-2 prose-p:leading-6 prose-strong:font-semibold prose-strong:text-[#9A5B2E] prose-ul:my-2 prose-ul:pl-5 prose-ol:my-2 prose-ol:pl-5 prose-li:my-1">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    ) : (
                      message.content
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-3">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-[#1C1D1B] text-[#F5F5F1]">
                    <Target size={14} strokeWidth={1.75} />
                  </div>
                  <div className="flex items-center gap-2 rounded-xl border border-[#E1DFD5] bg-white px-4 py-3 text-[13px] text-[#82806F]">
                    <span className="h-3 w-3 shrink-0 animate-spin rounded-full border-[1.5px] border-[#E1DFD5] border-t-[#9A5B2E] motion-reduce:animate-none" />
                    Comparing prices and specs…
                  </div>
                </div>
              )}

              <div ref={scrollAnchorRef} />
            </div>

            <form
              onSubmit={handleSubmit}
              className="flex items-center gap-2 border-t border-[#E1DFD5] p-3"
            >
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="What are you looking for?"
                aria-label="Describe what you're shopping for"
                className="min-w-0 flex-1 rounded-lg bg-[#F0EFEA] px-4 py-3 text-[14px] text-[#1C1D1B] outline-none placeholder:text-[#9C9A8E] focus-visible:ring-2 focus-visible:ring-[#9A5B2E]/40"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                aria-label="Send message"
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#1C1D1B] text-[#F5F5F1] transition-colors hover:bg-[#9A5B2E] focus-visible:ring-2 focus-visible:ring-[#9A5B2E]/40 disabled:cursor-not-allowed disabled:bg-[#D8D6CB] disabled:text-[#9C9A8E]"
              >
                <ArrowUp size={17} strokeWidth={2} />
              </button>
            </form>
          </div>

          {/* Starters */}
          <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            {starters.map((s) => (
              <button
                key={s.label}
                onClick={() => sendMessage(s.label)}
                disabled={loading}
                className="flex flex-1 items-center justify-between gap-3 rounded-lg border border-[#E1DFD5] bg-white px-4 py-2.5 text-left text-[13px] text-[#2B2A26] transition-colors hover:border-[#9A5B2E]/40 hover:bg-[#FBF3EE] focus-visible:ring-2 focus-visible:ring-[#9A5B2E]/40 disabled:opacity-40 sm:min-w-[220px]"
              >
                <span>{s.label}</span>
                <span className="shrink-0 text-[11px] text-[#9C9A8E]">{s.hint}</span>
              </button>
            ))}
          </div>
        </section>

        <footer className="mt-auto border-t border-[#E1DFD5] py-6 text-[12px] text-[#9C9A8E]">
          DealHunter is an assistant, not a merchant — always confirm price and
          stock on the retailer's site before buying.
        </footer>
      </div>
    </main>
  );
}