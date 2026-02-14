import { useEffect, useRef } from 'react';

const GalleryRow = ({ direction, images }: { direction: 'ltr' | 'rtl', images: string[] }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>(0);

  const initialTranaform = direction === 'rtl' ? 0 : 5000

  useEffect(() => {
    let offset = 0;
    const speed = 1;
    const imageWidth = 176; // h-40 (160px) + gap-4 (16px)
    const resetPoint = imageWidth * images.length;

    const animate = () => {
      if (direction === 'ltr') {
        // Move left
        offset -= speed;

        // Reset when we've scrolled one full set
        if (offset <= -resetPoint) {
          offset = 0;
        }
      } else {
        // Move right
        offset += speed;

        // Reset when we've scrolled one full set
        if (offset >= resetPoint) {
          offset = 0;
        }
      }

      if (containerRef.current) {
        containerRef.current.style.transform = `translateX(${initialTranaform + offset}px)`;
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [direction, images.length]);

  // Triple the images for seamless loop
  const displayImages = [...images, ...images, ...images];

  return (
    <div className="relative w-full overflow-hidden py-6">
      <div ref={containerRef} className="flex gap-4 will-change-transform">
        {displayImages.map((src, index) => (
          <img
            key={index}
            src={src}
            className="h-[120px] w-auto shrink-0 rounded-sm object-cover shadow-md"
            alt="travel"
          />
        ))}
      </div>
    </div>
  );
};

export default GalleryRow;