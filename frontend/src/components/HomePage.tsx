"use client";

import dynamic from "next/dynamic";

const HomeClient = dynamic(
  () => import("@/components/HomeClient").then((mod) => mod.HomeClient),
  { ssr: false },
);

export function HomePage() {
  return <HomeClient />;
}
