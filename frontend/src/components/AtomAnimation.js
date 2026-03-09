import { useEffect, useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import './AtomAnimation.css';

export default function AtomAnimation() {
  const containerRef = useRef(null);
  const [isMobile, setIsMobile] = useState(false);
  
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  const rotateX = useSpring(useTransform(mouseY, [-300, 300], [6, -6]), {
    stiffness: 150,
    damping: 20
  });
  const rotateY = useSpring(useTransform(mouseX, [-300, 300], [-6, 6]), {
    stiffness: 150,
    damping: 20
  });
  
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  const handleMouseMove = (e) => {
    if (isMobile || !containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    mouseX.set(e.clientX - centerX);
    mouseY.set(e.clientY - centerY);
  };
  
  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };
  
  return (
    <motion.div
      ref={containerRef}
      className="atom-container-refined"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div
        className="atom-3d-wrapper"
        style={{
          rotateX: isMobile ? 0 : rotateX,
          rotateY: isMobile ? 0 : rotateY,
        }}
      >
        {/* Cyan bloom behind atom */}
        <div className="atom-bloom" />
        
        <svg
          className="atom-svg-refined"
          viewBox="0 0 340 340"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Nucleus gradient */}
            <radialGradient id="nucleusGradient" cx="35%" cy="35%">
              <stop offset="0%" stopColor="#23ACD5" stopOpacity="1" />
              <stop offset="70%" stopColor="#1B8CA4" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#0E4A56" stopOpacity="0.85" />
            </radialGradient>
            
            {/* Glow filter for front segments */}
            <filter id="frontGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            {/* Blur filter for back segments */}
            <filter id="backBlur" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="0.6" />
            </filter>
            
            {/* Electron glow */}
            <filter id="electronGlow" x="-100%" y="-100%" width="300%" height="300%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            {/* Orbit path definitions */}
            <path
              id="orbit1Path"
              d="M 170,50 A 100,40 0 0,1 170,230 A 100,40 0 0,1 170,50 z"
              fill="none"
            />
            
            <path
              id="orbit2Path"
              d="M 215,80 A 100,40 60 0,1 125,260 A 100,40 60 0,1 215,80 z"
              fill="none"
            />
            
            <path
              id="orbit3Path"
              d="M 125,80 A 100,40 120 0,1 215,260 A 100,40 120 0,1 125,80 z"
              fill="none"
            />
          </defs>
          
          {/* Rotating orbits group */}
          <g className="orbits-container-refined">
            {/* BACK SEGMENTS - rendered first (z-index behind) */}
            <g className="back-segments">
              {/* Orbit 1 back half */}
              <path
                d="M 170,50 A 100,40 0 0,1 170,230"
                fill="none"
                stroke="#23ACD5"
                strokeWidth="1.5"
                opacity="0.28"
                className="orbit-back"
                filter="url(#backBlur)"
              />
              {/* Orbit 2 back half */}
              <path
                d="M 215,80 A 100,40 60 0,1 125,260"
                fill="none"
                stroke="#23ACD5"
                strokeWidth="1.5"
                opacity="0.25"
                className="orbit-back"
                filter="url(#backBlur)"
              />
              {/* Orbit 3 back half */}
              <path
                d="M 125,80 A 100,40 120 0,1 215,260"
                fill="none"
                stroke="#23ACD5"
                strokeWidth="1.5"
                opacity="0.3"
                className="orbit-back"
                filter="url(#backBlur)"
              />
            </g>
            
            {/* NUCLEUS - in the middle layer */}
            <g className="nucleus-layer">
              {/* Shadow */}
              <ellipse
                cx="172"
                cy="173"
                rx="13"
                ry="9"
                fill="#000000"
                opacity="0.2"
                filter="url(#backBlur)"
              />
              {/* Main nucleus */}
              <circle
                cx="170"
                cy="170"
                r="15"
                fill="url(#nucleusGradient)"
                className="nucleus-refined"
              />
              {/* Highlight */}
              <circle
                cx="164"
                cy="164"
                r="5"
                fill="#ffffff"
                opacity="0.55"
                className="nucleus-highlight-refined"
              />
            </g>
            
            {/* FRONT SEGMENTS - rendered last (z-index on top) */}
            <g className="front-segments">
              {/* Orbit 1 front half */}
              <path
                d="M 170,230 A 100,40 0 0,1 170,50"
                fill="none"
                stroke="#23ACD5"
                strokeWidth="2.5"
                opacity="0.9"
                className="orbit-front"
                filter="url(#frontGlow)"
              />
              {/* Orbit 2 front half */}
              <path
                d="M 125,260 A 100,40 60 0,1 215,80"
                fill="none"
                stroke="#23ACD5"
                strokeWidth="2.5"
                opacity="0.85"
                className="orbit-front"
                filter="url(#frontGlow)"
              />
              {/* Orbit 3 front half */}
              <path
                d="M 215,260 A 100,40 120 0,1 125,80"
                fill="none"
                stroke="#23ACD5"
                strokeWidth="2.5"
                opacity="0.88"
                className="orbit-front"
                filter="url(#frontGlow)"
              />
            </g>
            
            {/* ELECTRONS - path-locked using animateMotion */}
            <g className="electrons-layer">
              {/* Electron 1 */}
              <circle 
                r="4.5" 
                fill="#23ACD5" 
                className="electron-refined"
                filter="url(#electronGlow)"
              >
                <animateMotion dur="6s" repeatCount="indefinite">
                  <mpath href="#orbit1Path" />
                </animateMotion>
              </circle>
              
              {/* Electron 2 */}
              <circle 
                r="4.5" 
                fill="#23ACD5" 
                className="electron-refined"
                filter="url(#electronGlow)"
              >
                <animateMotion dur="9s" repeatCount="indefinite">
                  <mpath href="#orbit2Path" />
                </animateMotion>
              </circle>
              
              {/* Electron 3 */}
              <circle 
                r="4.5" 
                fill="#23ACD5" 
                className="electron-refined"
                filter="url(#electronGlow)"
              >
                <animateMotion dur="12s" repeatCount="indefinite">
                  <mpath href="#orbit3Path" />
                </animateMotion>
              </circle>
            </g>
          </g>
        </svg>
      </motion.div>
    </motion.div>
  );
}
