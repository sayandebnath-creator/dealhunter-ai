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
  ExternalLink,
  Star,
  ShoppingBag,
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

type Product = {
  name: string;
  price?: number | null;
  currency?: string | null;
  ram?: number | null;
  storage?: string | number | null;
  processor?: string | null;
  battery_hours?: number | null;
  battery_text?: string | null;
  rating?: number | null;
  reviews?: number | null;
  url?: string | null;
  source?: string | null;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  products?: Product[];
  isError?: boolean;
};

const starters = [
  {
    label: "Laptop under ₹70,000 for programming",
    hint: "budget · laptops",
  },
  {
    label: "Laptop under ₹60,000 with 16GB RAM",
    hint: "budget · laptops",
  },
  {
    label: "Laptop with great battery life",
    hint: "priority · laptops",
  },
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

function formatPrice(
  price?: number | null,
  currency?: string | null
): string {
  if (price == null) return "Price unavailable";

  const symbol = currency === "INR" || !currency ? "₹" : currency;

  return `${symbol}${price.toLocaleString("en-IN")}`;
}

function ProductCard({
  product,
  index,
}: {
  product: Product;
  index: number;
}) {
  return (
    <article className="group overflow-hidden rounded-xl border border-[#E1DFD5] bg-[#FCFCF9] transition-all duration-200 hover:-translate-y-0.5 hover:border-[#C9C5B9] hover:shadow-[0_10px_30px_-18px_rgba(28,29,27,0.25)]">
      {/* Card header */}
      <div className="border-b border-[#E8E6DD] px-4 py-4 sm:px-5">
        <div className="mb-3 flex items-center justify-between gap-3">
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-[#1C1D1B] text-xs font-semibold text-[#F5F5F1]">
            {index + 1}
          </span>

          {product.source && (
            <span className="max-w-[180px] truncate text-[11px] text-[#9C9A8E]">
              {product.source}
            </span>
          )}
        </div>

        <h3
          className="line-clamp-3 text-[15px] font-medium leading-6 text-[#1C1D1B]"
          style={{ fontFamily: "var(--font-inter)" }}
        >
          {product.name}
        </h3>
      </div>

      {/* Price */}
      <div className="px-4 pt-4 sm:px-5">
        <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-[#9C9A8E]">
          Current price
        </p>

        <p
          className="mt-1 text-[23px] font-semibold tracking-tight text-[#9A5B2E]"
          style={{ fontFamily: "var(--font-fraunces)" }}
        >
          {formatPrice(product.price, product.currency)}
        </p>
      </div>

      {/* Specs */}
      <div className="px-4 py-4 sm:px-5">
        <div className="grid grid-cols-2 gap-2">
          {product.ram != null && (
            <Spec label="RAM" value={`${product.ram} GB`} />
          )}

          {product.storage != null && (
            <Spec label="Storage" value={`${product.storage}`} />
          )}

          {product.processor && (
            <div className="col-span-2">
              <Spec label="Processor" value={product.processor} />
            </div>
          )}

          {product.battery_hours != null && (
            <Spec
              label="Battery"
              value={`${product.battery_hours} hrs`}
            />
          )}

          {product.battery_text && (
            <Spec
              label="Battery"
              value={product.battery_text}
            />
          )}

          {product.rating != null && (
            <div className="flex items-center gap-2 rounded-lg bg-[#F1F0EA] px-3 py-2">
              <Star
                size={13}
                strokeWidth={1.8}
                className="fill-[#9A5B2E] text-[#9A5B2E]"
              />

              <div>
                <p className="text-[10px] uppercase tracking-wide text-[#9C9A8E]">
                  Rating
                </p>

                <p className="text-[12px] font-medium text-[#2B2A26]">
                  {product.rating}
                  {product.reviews != null && (
                    <span className="ml-1 font-normal text-[#8A887E]">
                      ({product.reviews.toLocaleString("en-IN")})
                    </span>
                  )}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action */}
      <div className="border-t border-[#E8E6DD] bg-[#F7F7F2] px-4 py-3 sm:px-5">
        {product.url ? (
          <a
            href={product.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#1C1D1B] px-4 py-2.5 text-[12px] font-medium text-[#F5F5F1] transition-colors hover:bg-[#9A5B2E]"
          >
            View Product
            <ExternalLink size={13} strokeWidth={1.8} />
          </a>
        ) : (
          <div className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#E6E4DB] px-4 py-2.5 text-[12px] text-[#8A887E]">
            Product link unavailable
          </div>
        )}
      </div>
    </article>
  );
}

function Spec({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg bg-[#F1F0EA] px-3 py-2">
      <p className="text-[10px] uppercase tracking-wide text-[#9C9A8E]">
        {label}
      </p>

      <p className="mt-0.5 line-clamp-2 text-[12px] font-medium leading-4 text-[#2B2A26]">
        {value}
      </p>
    </div>
  );
}

function AssistantContent({
  content,
  products,
}: {
  content: string;
  products?: Product[];
}) {
  return (
    <div className="space-y-5">
      {/* Recommendation / explanation */}
      <div className="prose prose-sm max-w-none text-[#2B2A26]">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1
                className="mb-3 mt-0 border-b border-[#E8E6DD] pb-3 text-[20px] font-semibold tracking-tight text-[#1C1D1B]"
                style={{ fontFamily: "var(--font-fraunces)" }}
              >
                {children}
              </h1>
            ),

            h2: ({ children }) => (
              <h2
                className="mb-3 mt-6 flex items-center gap-2 border-b border-[#E8E6DD] pb-2 text-[16px] font-semibold text-[#1C1D1B]"
                style={{ fontFamily: "var(--font-fraunces)" }}
              >
                {children}
              </h2>
            ),

            h3: ({ children }) => (
              <h3 className="mb-2 mt-5 text-[14px] font-semibold text-[#1C1D1B]">
                {children}
              </h3>
            ),

            p: ({ children }) => (
              <p className="my-2 text-[13px] leading-6 text-[#5C5B54]">
                {children}
              </p>
            ),

            strong: ({ children }) => (
              <strong className="font-semibold text-[#9A5B2E]">
                {children}
              </strong>
            ),

            ul: ({ children }) => (
              <ul className="my-3 space-y-2 pl-5 text-[13px] leading-6 marker:text-[#9A5B2E]">
                {children}
              </ul>
            ),

            ol: ({ children }) => (
              <ol className="my-4 space-y-3 pl-6 text-[13px] leading-6 marker:font-semibold marker:text-[#9A5B2E]">
                {children}
              </ol>
            ),

            li: ({ children }) => (
              <li className="pl-1 text-[#4D4C46]">
                {children}
              </li>
            ),

            blockquote: ({ children }) => (
              <blockquote className="my-4 rounded-lg border-l-2 border-[#9A5B2E] bg-[#FBF3EE] px-4 py-3 text-[13px] text-[#6B4938]">
                {children}
              </blockquote>
            ),

            code: ({ children }) => (
              <code className="rounded bg-[#F0EFEA] px-1.5 py-0.5 text-[12px] text-[#9A5B2E]">
                {children}
              </code>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </div>

      {/* Product section */}
      {products && products.length > 0 && (
        <section className="border-t border-[#E1DFD5] pt-5">
          <div className="mb-4 flex items-end justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <ShoppingBag
                  size={15}
                  strokeWidth={1.8}
                  className="text-[#9A5B2E]"
                />

                <h2
                  className="text-[17px] font-semibold tracking-tight text-[#1C1D1B]"
                  style={{ fontFamily: "var(--font-fraunces)" }}
                >
                  Product shortlist
                </h2>
              </div>

              <p className="mt-1 text-[12px] text-[#82806F]">
                {products.length} matching{" "}
                {products.length === 1 ? "product" : "products"} found
              </p>
            </div>

            <span className="hidden rounded-full border border-[#E1DFD5] bg-[#F7F7F2] px-3 py-1 text-[10px] uppercase tracking-[0.08em] text-[#82806F] sm:block">
              Compared options
            </span>
          </div>

          <div className="grid gap-3 lg:grid-cols-2">
            {products.map((product, index) => (
              <ProductCard
                key={`${product.name}-${index}`}
                product={product}
                index={index}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

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
    scrollAnchorRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  async function sendMessage(message?: string) {
    const text = (message ?? input).trim();

    if (!text || loading) return;

    setInput("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text,
      },
    ]);

    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: text,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          products: Array.isArray(data.products)
            ? data.products
            : [],
        },
      ]);
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
      {/* Background */}
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
              <span className="italic text-[#9A5B2E]">
                Start with a question.
              </span>
            </h1>

            <p className="mt-6 max-w-md text-[15px] leading-7 text-[#5C5B54]">
              Most product search makes you do the comparing. DealHunter reads
              specs and prices for you, then explains the trade-offs in plain
              terms — so you spend less time deciding and more time using
              whatever you bought.
            </p>
          </div>

          <div className="flex flex-col justify-end gap-3 border-t border-[#E1DFD5] pt-6 md:border-l md:border-t-0 md:pl-10 md:pt-0">
            {steps.map(({ icon: Icon, title, description }) => (
              <div key={title} className="flex gap-3">
                <Icon
                  size={16}
                  strokeWidth={1.75}
                  className="mt-1 shrink-0 text-[#9A5B2E]"
                />

                <div>
                  <p className="text-[13px] font-medium text-[#1C1D1B]">
                    {title}
                  </p>

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
              className="max-h-[720px] min-h-[280px] space-y-5 overflow-y-auto p-5 sm:p-7"
            >
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === "user"
                      ? "flex-row-reverse"
                      : ""
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
                    className={`max-w-[92%] rounded-xl px-4 py-3 text-[14px] leading-6 sm:max-w-[88%] ${
                      message.role === "user"
                        ? "bg-[#1C1D1B] text-[#F5F5F1]"
                        : message.isError
                        ? "border border-[#EAD3C6] bg-[#FBF3EE] text-[#7A3A22]"
                        : "border border-[#E1DFD5] bg-white text-[#2B2A26]"
                    }`}
                  >
                    {message.role === "assistant" ? (
                      message.isError ? (
                        <p className="text-[13px] leading-6">
                          {message.content}
                        </p>
                      ) : (
                        <AssistantContent
                          content={message.content}
                          products={message.products}
                        />
                      )
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

            {/* Input */}
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
                <span className="shrink-0 text-[11px] text-[#9C9A8E]">
                  {s.hint}
                </span>
              </button>
            ))}
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-auto border-t border-[#E1DFD5] py-6 text-[12px] text-[#9C9A8E]">
          DealHunter is an assistant, not a merchant — always confirm price and
          stock on the retailer&apos;s site before buying.
        </footer>
      </div>
    </main>
  );
}