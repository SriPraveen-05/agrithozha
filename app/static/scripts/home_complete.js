// Complete Home Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        offset: 100
    });

    // Counter animation for stats
    function animateCounters() {
        const counters = document.querySelectorAll('.stat-number[data-count]');
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-count'));
            const duration = 2000; // 2 seconds
            const increment = target / (duration / 16); // 60fps
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                counter.textContent = Math.floor(current);
            }, 16);
        });
    }

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                
                // Trigger counter animation for stats section
                if (entry.target.classList.contains('stats-section')) {
                    animateCounters();
                }
            }
        });
    }, observerOptions);

    // Observe all animated elements
    document.querySelectorAll('.feature-card, .service-card, .stat-card, .testimonial-card').forEach(el => {
        observer.observe(el);
    });

    // Create particle effect
    function createParticles() {
        const particlesContainer = document.getElementById('particles');
        if (!particlesContainer) return;

        const particleCount = 50;
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: 2px;
                height: 2px;
                background: rgba(255, 255, 255, 0.5);
                border-radius: 50%;
                pointer-events: none;
                animation: particleFloat ${5 + Math.random() * 10}s linear infinite;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation-delay: ${Math.random() * 5}s;
            `;
            particlesContainer.appendChild(particle);
        }

        // Add CSS for particle animation
        const particleStyle = document.createElement('style');
        particleStyle.textContent = `
            @keyframes particleFloat {
                0% {
                    transform: translateY(100vh) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                }
                90% {
                    opacity: 1;
                }
                100% {
                    transform: translateY(-100vh) rotate(360deg);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(particleStyle);
    }

    // Initialize particles
    createParticles();

    // Parallax effect for hero shapes
    function handleParallax() {
        const shapes = document.querySelectorAll('.shape');
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;

        shapes.forEach((shape, index) => {
            const speed = 0.5 + (index * 0.1);
            shape.style.transform = `translateY(${rate * speed}px)`;
        });
    }

    // Throttled scroll handler
    let ticking = false;
    function updateParallax() {
        if (!ticking) {
            requestAnimationFrame(() => {
                handleParallax();
                ticking = false;
            });
            ticking = true;
        }
    }

    window.addEventListener('scroll', updateParallax);

    // Add hover effects to cards
    document.querySelectorAll('.card, .feature-card, .service-card, .testimonial-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add ripple effect to buttons
    function createRipple(event) {
        const button = event.currentTarget;
        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;

        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
        circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
        circle.classList.add('ripple');

        const ripple = button.getElementsByClassName('ripple')[0];
        if (ripple) {
            ripple.remove();
        }

        button.appendChild(circle);
    }

    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', createRipple);
    });

    // Add CSS for ripple effect
    const style = document.createElement('style');
    style.textContent = `
        .btn {
            position: relative;
            overflow: hidden;
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple 600ms linear;
            pointer-events: none;
        }
        
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Add loading states to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.type === 'submit') {
                return; // Don't add loading to submit buttons
            }
            
            // Add loading state
            const originalContent = this.innerHTML;
            this.innerHTML = '<span class="loading"></span> Processing...';
            this.disabled = true;
            
            // Remove loading state after 2 seconds
            setTimeout(() => {
                this.innerHTML = originalContent;
                this.disabled = false;
            }, 2000);
        });
    });

    // Add scroll progress indicator
    function updateScrollProgress() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.body.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        
        // Create progress bar if it doesn't exist
        let progressBar = document.querySelector('.scroll-progress');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.className = 'scroll-progress';
            progressBar.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 0%;
                height: 3px;
                background: linear-gradient(90deg, var(--primary-500), var(--secondary-500));
                z-index: 9999;
                transition: width 0.1s ease;
            `;
            document.body.appendChild(progressBar);
        }
        
        progressBar.style.width = scrollPercent + '%';
    }

    window.addEventListener('scroll', updateScrollProgress);

    // Add floating animation to hero shapes
    function addFloatingAnimation() {
        const shapes = document.querySelectorAll('.shape');
        shapes.forEach((shape, index) => {
            const delay = index * 1000; // Stagger the animations
            setTimeout(() => {
                shape.style.animation = `float ${3 + index}s ease-in-out infinite`;
            }, delay);
        });
    }

    addFloatingAnimation();

    // Add mouse parallax effect
    function handleMouseParallax(e) {
        const shapes = document.querySelectorAll('.shape');
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;

        shapes.forEach((shape, index) => {
            const speed = 0.5 + (index * 0.2);
            const xPos = (x - 0.5) * speed * 50;
            const yPos = (y - 0.5) * speed * 50;
            shape.style.transform = `translate(${xPos}px, ${yPos}px)`;
        });
    }

    document.addEventListener('mousemove', handleMouseParallax);

    // Add scroll-triggered animations
    function addScrollAnimations() {
        const animatedElements = document.querySelectorAll('.feature-card, .service-card, .stat-card, .testimonial-card');
        
        animatedElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(50px)';
            element.style.transition = 'all 0.6s ease';
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        setTimeout(() => {
                            entry.target.style.opacity = '1';
                            entry.target.style.transform = 'translateY(0)';
                        }, index * 100); // Stagger the animations
                    }
                });
            }, { threshold: 0.1 });
            
            observer.observe(element);
        });
    }

    addScrollAnimations();

    // Add smooth reveal animation for text
    function revealText() {
        const textElements = document.querySelectorAll('.hero-title, .hero-subtitle');
        
        textElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'all 0.8s ease';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 300);
        });
    }

    revealText();

    // Add typing effect for hero title
    function typeWriter(element, text, speed = 100) {
        let i = 0;
        element.innerHTML = '';
        
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }

    // Initialize typing effect if element exists
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const originalText = heroTitle.textContent;
        // Uncomment the line below to enable typing effect
        // typeWriter(heroTitle, originalText, 50);
    }

    // Add gradient animation to hero title
    function animateGradient() {
        const gradientText = document.querySelector('.gradient-text');
        if (gradientText) {
            setInterval(() => {
            const colors = [
                'linear-gradient(135deg, #84cc16, #65a30d)',
                'linear-gradient(135deg, #22c55e, #16a34a)',
                'linear-gradient(135deg, #14b8a6, #0d9488)',
                'linear-gradient(135deg, #bef264, #a3e635)'
            ];
                const randomColor = colors[Math.floor(Math.random() * colors.length)];
                gradientText.style.background = randomColor;
                gradientText.style.webkitBackgroundClip = 'text';
                gradientText.style.webkitTextFillColor = 'transparent';
                gradientText.style.backgroundClip = 'text';
            }, 3000);
        }
    }

    animateGradient();

    // Add hover effects to service cards
    document.querySelectorAll('.service-card').forEach(card => {
        const overlay = card.querySelector('.service-overlay');
        const btn = card.querySelector('.service-btn');
        
        card.addEventListener('mouseenter', () => {
            if (overlay) overlay.style.opacity = '1';
            if (btn) btn.style.transform = 'scale(1.1)';
        });
        
        card.addEventListener('mouseleave', () => {
            if (overlay) overlay.style.opacity = '0';
            if (btn) btn.style.transform = 'scale(1)';
        });
    });

    // Add scroll-triggered counter animation
    function animateCountersOnScroll() {
        const counters = document.querySelectorAll('.stat-number[data-count]');
        
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.getAttribute('data-count'));
                    const duration = 2000;
                    const increment = target / (duration / 16);
                    let current = 0;
                    
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= target) {
                            current = target;
                            clearInterval(timer);
                        }
                        counter.textContent = Math.floor(current);
                    }, 16);
                    
                    counterObserver.unobserve(counter);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }

    animateCountersOnScroll();

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading animation to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.type === 'submit') {
                const originalContent = this.innerHTML;
                this.innerHTML = '<span class="loading"></span> Processing...';
                this.disabled = true;
                
                setTimeout(() => {
                    this.innerHTML = originalContent;
                    this.disabled = false;
                }, 2000);
            }
        });
    });

    // Add CSS for loading animation
    const loadingStyle = document.createElement('style');
    loadingStyle.textContent = `
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(loadingStyle);

    console.log('🚀 Complete Home Page JavaScript loaded successfully!');
});
