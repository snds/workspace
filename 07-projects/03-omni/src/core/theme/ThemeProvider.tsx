import { useEffect } from 'react';
import { OMNI_TOKENS } from './omniTokens';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const root = document.documentElement;
    for (const [path, token] of Object.entries(OMNI_TOKENS)) {
      if (token.$type === 'color' || token.$type === 'dimension') {
        const varName = `--${path.replace(/\./g, '-')}`;
        root.style.setProperty(varName, String(token.$value));
      }
    }
  }, []);

  return <>{children}</>;
}
