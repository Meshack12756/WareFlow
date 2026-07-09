// src/components/Animations/AnimatedCard.jsx
import React, { useRef, useEffect } from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(useGSAP);

const AnimatedCard = ({ title, value, icon, color, delay = 0, children }) => {
  const cardRef = useRef(null);

  // Animate on mount – no scrollTrigger
  useGSAP(() => {
    
    gsap.set(cardRef.current, {opacity: 0, y: 30});

    gsap.to(cardRef.current, {
      opacity: 1,
      y: 0,
      duration: 0.8,
      delay: delay,
      ease: 'power3.out',
    });
  }, { scope: cardRef, dependencies: [delay] });

  // Counter animation for values
  useEffect(() => {
    if (!value) return;
    const el = cardRef.current?.querySelector('.card-value');
    if (!el) return;

    const numericValue = typeof value === 'string' ? parseFloat(value.replace(/[^0-9.]/g, '')) : value;
    if (isNaN(numericValue)) return;

    let start = 0;
    const duration = 1500;
    const step = Math.max(1, Math.floor(numericValue / 60));

    const interval = setInterval(() => {
      start += step;
      if (start >= numericValue) {
        start = numericValue;
        clearInterval(interval);
      }
      el.textContent = typeof value === 'string' ? `${start.toFixed(2)}` : start;
    }, duration / 60);

    return () => clearInterval(interval);
  }, [value]);

  return (
    <Card ref={cardRef} sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
      <Box
        sx={{
          position: 'absolute',
          top: -20,
          right: -20,
          width: 80,
          height: 80,
          borderRadius: '50%',
          backgroundColor: color,
          opacity: 0.08,
        }}
      />
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h5" component="div" className="card-value" sx={{ fontWeight: 600 }}>
              {value || 0}
            </Typography>
          </Box>
          <Box sx={{ color: color, opacity: 0.8 }}>{icon}</Box>
        </Box>
        {children && <Box mt={2}>{children}</Box>}
      </CardContent>
    </Card>
  );
};

export default AnimatedCard;