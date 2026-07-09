// src/components/Animations/PageTransition.jsx
import React, { useRef } from 'react';
import { Box } from '@mui/material';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';

const PageTransition = ({ children }) => {
  const containerRef = useRef(null);

  useGSAP(() => {
    gsap.from(containerRef.current, {
      opacity: 0,
      y: 20,
      duration: 0.6,
      ease: 'power2.out',
      clearProps: 'all',
    });
  }, { scope: containerRef });

  return <Box ref={containerRef}>{children}</Box>;
};

export default PageTransition;