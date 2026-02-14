import React from 'react';

const BackgroundPattern: React.FC = () => {
  return (
    <div 
      className="fixed inset-0 -z-10 opacity-[0.04] pointer-events-none"
      style={{
        backgroundImage: `
          radial-gradient(#00695C 2px, transparent 2px),
          radial-gradient(#2E7D32 2px, transparent 2px)
        `,
        backgroundSize: '30px 30px',
        backgroundPosition: '0 0, 15px 15px'
      }}
    />
  );
};

export default BackgroundPattern;