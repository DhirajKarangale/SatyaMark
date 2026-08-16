import { memo } from "react";

function FAQ() {
  const faqs = [
    {
      q: "What is SatyaMark and how does it act as an open source content verification platform?",
      a: "SatyaMark is an open source trust infrastructure and content credibility platform designed to combat online manipulation. It functions as a multi modal verification system, offering explainable verification and trust signals rather than acting as a black-box fake news detection tool. By utilizing a distributed verification architecture, it provides real-time content verification natively inside social feeds to aid in misinformation detection."
    },
    {
      q: "How does the fact checking API handle digital content verification?",
      a: "The fact checking API acts as a decoupled verification layer that processes images and text in the background. It is built to serve as a scalable open source fact checker that gives users transparent, evidence-backed reasoning for every piece of content evaluated."
    },
    {
      q: "How do I integrate the React content verification SDK into my web application?",
      a: "Developers can easily embed the satyamark-react npm package directly into their projects. This React fact checking library serves as a powerful DOM scanning SDK that performs real time DOM verification. It injects React UI trust indicators right next to the content on the screen."
    },
    {
      q: "Does the satyamark-react package slow down the host UI?",
      a: "No. Because it is a WebSocket React SDK, it delivers zero-polling UI updates. This allows for automated UI fact checking and web components fact checking strictly in the background, without freezing or blocking the host application."
    },
    {
      q: "How does the Node.js verification engine handle asynchronous AI orchestration?",
      a: "The backend operates as an Express verification orchestrator supported by a high concurrency Node.js backend and a real time WebSocket server. To process heavy AI jobs efficiently, it utilizes a Redis Streams job queue. By employing a memory aware Redis queue with dynamic load balancing Redis logic, tasks are safely routed to a background worker queue so the main server never crashes."
    },
    {
      q: "How does cryptographic verification caching improve response times for viral content?",
      a: "To prevent redundant processing, the system uses PostgreSQL SHA-256 deduplication for content hash caching. This Relational persistence fact checking allows for fast cache hit verification. When an identical claim or image is submitted, the post content deduplication system bypasses the AI worker queue entirely, returning the cached result instantly."
    },
    {
      q: "How does the LangGraph fact checking pipeline evaluate text claims?",
      a: "The text verification process uses a Directed Acyclic Graph AI model. The LLM fact checking engine first runs subjectivity detection AI to isolate objective facts, followed by automated claim extraction. It then utilizes a Milvus RAG evidence retrieval and FAISS vector search system for automated evidence retrieval. If internal knowledge bases are insufficient, it triggers live web scraping verification using a Google Search API RAG setup powered by Anthropic Claude verification."
    },
    {
      q: "What open source image forensics are included in the deepfake detection API?",
      a: "The microservice AI pipeline includes comprehensive AI generated image detection. Rather than relying solely on a Sightengine alternative or Truthscan deepfake analysis, it performs deep pixel level synthesis detection. This includes running Error Level Analysis ELA, PRNU analysis python scripts for sensor pattern noise detection, diffusion latent analysis, Benfords law image forensics, and C2PA content provenance tracking to ensure highly accurate detection of manipulated media."
    },
    {
      q: "Can I use SatyaMark as a standalone fact checking engine for a non-React application?",
      a: "Yes, it is built to serve as a comprehensive digital trust infrastructure. Even if you do not use our frontend tools, the core fact checking API allows you to send raw payloads directly to the Node.js verification engine. This means you can leverage our digital content verification capabilities and distributed verification architecture across iOS, Android, or standard HTML web applications."
    },
    {
      q: "Why should I install satyamark-react instead of building my own React content verification SDK?",
      a: "Building a custom real time DOM verification layer that doesn't cause infinite re-renders is incredibly difficult. The satyamark-react package provides a battle-tested React content verification SDK right out of the box. It securely handles the DOM scanning SDK logic and manages the WebSocket lifecycle to deliver zero-polling UI updates, making the integration of React UI trust indicators a seamless, two-line process."
    },
    {
      q: "How does the system handle viral misinformation without crashing the AI worker queue?",
      a: "Viral content is handled through strict cryptographic verification caching. Before any expensive compute happens, the high concurrency Node.js backend performs a hash check. By utilizing PostgreSQL SHA-256 deduplication, the system ensures fast cache hit verification. This post content deduplication means that if a million users see the same viral image, the AI worker queue only processes it once, instantly returning the cached result to all other clients."
    },
    {
      q: "What makes the LangGraph fact checking pipeline more accurate than a standard LLM wrapper?",
      a: "Standard LLMs are prone to hallucination, which is unacceptable for digital content verification. Our LLM fact checking engine solves this by strictly following a Directed Acyclic Graph AI workflow. It enforces subjectivity detection AI and automated claim extraction first. Then, it utilizes FAISS vector search and live web scraping verification to guarantee that the final verdict is strictly based on automated evidence retrieval, rather than the LLM's internal weights."
    },
    {
      q: "Is the deepfake detection API a paid service or a true open source alternative?",
      a: "SatyaMark provides a completely free, open source image forensics toolkit that acts as a highly capable Sightengine alternative or Truthscan deepfake analysis replacement. Instead of basic metadata checks, the microservice AI pipeline executes deep pixel level synthesis detection. By combining C2PA content provenance tracking with Benfords law image forensics and diffusion latent analysis, it provides enterprise-grade AI generated image detection that anyone can host on their own servers."
    }
  ];

  const faqData = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.q,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.a
      }
    }))
  };

  return (
    <section className="py-20 bg-slate-950 border-t border-white/10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqData) }}
      />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Learn more about SatyaMark's trust infrastructure, AI verification pipelines, and open source forensics.
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <details 
              key={index}
              className="group bg-slate-900/50 border border-white/10 rounded-xl overflow-hidden [&_summary::-webkit-details-marker]:hidden"
            >
              <summary className="flex items-center justify-between cursor-pointer p-6 font-semibold text-white hover:text-cyan-400 transition-colors">
                <span>{faq.q}</span>
                <span className="transition group-open:rotate-180">
                  <svg fill="none" height="24" shapeRendering="geometricPrecision" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path></svg>
                </span>
              </summary>
              <div className="p-6 pt-0 text-gray-400 leading-relaxed border-t border-white/5 mt-2">
                <p className="mt-4">{faq.a}</p>
              </div>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}

export default memo(FAQ);
