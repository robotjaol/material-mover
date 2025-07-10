import './globals.css';

export const metadata = {
  title: 'Pallet Flow Diagnostic',
  description: 'Real-Time Predictive Pallet Flow Diagnostic Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-glass min-h-screen">{children}</body>
    </html>
  );
} 