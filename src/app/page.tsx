import { Benefits } from "@/components/sections/Benefits";
import { Faq } from "@/components/sections/Faq";
import { FinalCta } from "@/components/sections/FinalCta";
import { Gallery } from "@/components/sections/Gallery";
import { Hero } from "@/components/sections/Hero";
import { HowItWorks } from "@/components/sections/HowItWorks";
import { Stats } from "@/components/sections/Stats";
import { Testimonials } from "@/components/sections/Testimonials";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";

export default function Home() {
  return (
    <>
      <a
        href="#main"
        className="focus-ring fixed left-4 top-4 z-50 -translate-y-20 rounded-full border border-line bg-panel px-4 py-2 text-sm text-text transition focus:translate-y-0"
      >
        Перейти к содержанию
      </a>
      <Header />
      <main id="main">
        <Hero />
        <Benefits />
        <HowItWorks />
        <Testimonials />
        <Gallery />
        <Stats />
        <Faq />
        <FinalCta />
      </main>
      <Footer />
    </>
  );
}
