import React, { useEffect, useRef } from 'react';
import './AutoScrollGallery.css';

const imageUrls = [
	'https://i.scdn.co/image/ab67616d0000b273a8d74e789b99484e0e169001',
    'https://i.scdn.co/image/ab67616d0000b2735998097d9467eccb3e99b8c1',
    'https://i.scdn.co/image/ab67616d0000b273b2592bea12d840fd096ef965',
    'https://i.scdn.co/image/ab67616d0000b27326d64b6150aa3d9b6b67d857',
'https://i.scdn.co/image/ab67616d0000b273cd945b4e3de57edd28481a3f'
];

export default function AutoScrollGallery() {
  const scrollRef = useRef(null);

  useEffect(() => {
    const container = scrollRef.current;
    let scrollInterval;

    const startScrolling = () => {
      scrollInterval = setInterval(() => {
        if (!container) return;
        container.scrollBy({ left: 1, behavior: 'smooth' });

        // Reset scroll if at end
        if (
          container.scrollLeft + container.clientWidth >=
          container.scrollWidth - 1
        ) {
          container.scrollTo({ left: 0 });
        }
      }, 32); // ~60fps
    };

    startScrolling();

    return () => clearInterval(scrollInterval);
  }, []);

  return (
    <div className="scroll-container" ref={scrollRef}>
      {/* Duplicate images to help with smooth looping */}
      {[...imageUrls, ...imageUrls].map((url, index) => (
        <img key={index} src={url} alt={`img-${index}`} className="gallery-img" />
      ))}
    </div>
  );
}
