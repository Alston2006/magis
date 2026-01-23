// MAGIS - Premium Collector Cakes | JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Loading Screen
    const loadingScreen = document.getElementById('loadingScreen');
    setTimeout(() => loadingScreen.classList.add('hidden'), 2500);

    // Custom Cursor
    const cursorDot = document.querySelector('.cursor-dot');
    const cursorRing = document.querySelector('.cursor-ring');
    let mouseX = 0, mouseY = 0, ringX = 0, ringY = 0;

    document.addEventListener('mousemove', e => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        cursorDot.style.left = mouseX + 'px';
        cursorDot.style.top = mouseY + 'px';
    });

    function animateCursor() {
        ringX += (mouseX - ringX) * 0.15;
        ringY += (mouseY - ringY) * 0.15;
        cursorRing.style.left = ringX + 'px';
        cursorRing.style.top = ringY + 'px';
        requestAnimationFrame(animateCursor);
    }
    animateCursor();

    // Cursor hover effects
    document.querySelectorAll('a, button, .product-card, .collection-card').forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursorRing.style.transform = 'translate(-50%, -50%) scale(1.5)';
            cursorRing.style.borderColor = '#8b0000';
        });
        el.addEventListener('mouseleave', () => {
            cursorRing.style.transform = 'translate(-50%, -50%) scale(1)';
            cursorRing.style.borderColor = '#f5f5f5';
        });
    });

    // Navigation
    const nav = document.querySelector('.nav');
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');

    window.addEventListener('scroll', () => {
        nav.classList.toggle('scrolled', window.scrollY > 50);
    });

    menuToggle.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
        menuToggle.classList.toggle('active');
    });

    /* navLinks.forEach(link => {
         link.addEventListener('click', () => {
             mobileMenu.classList.remove('active');
             menuToggle.classList.remove('active');
             navLinks.forEach(l => l.classList.remove('active'));
             document.querySelectorAll(`[href="${link.getAttribute('href')}"]`).forEach(l => l.classList.add('active'));
         });
     }); */
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // close mobile menu
            mobileMenu.classList.remove('active');
            menuToggle.classList.remove('active');

            // active class handling
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });


    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', e => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    // Parallax Effects
    const parallaxElements = document.querySelectorAll('.parallax-element');
    const parallaxBg = document.querySelectorAll('.parallax-bg');

    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;

        parallaxElements.forEach(el => {
            const speed = el.dataset.speed || 0.05;
            const rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                el.style.transform = `translateY(${scrollY * speed}px)`;
            }
        });

        parallaxBg.forEach(bg => {
            const rect = bg.parentElement.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                bg.style.transform = `translateY(${scrollY * 0.03}px)`;
            }
        });
    });

    // Scroll Animations
    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = entry.target.dataset.delay || 0;
                setTimeout(() => entry.target.classList.add('visible'), delay * 1000);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-in, .fade-slide-up, .fade-slide-left, .fade-slide-right').forEach(el => observer.observe(el));

    // Process Timeline Animation
    const processSteps = document.querySelectorAll('.process-step');
    const timelineProgress = document.querySelector('.timeline-progress');

    const processObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const step = parseInt(entry.target.dataset.step);
                entry.target.classList.add('active');
                if (timelineProgress) {
                    timelineProgress.style.height = `${(step / processSteps.length) * 100}%`;
                }
            }
        });
    }, { threshold: 0.5 });

    processSteps.forEach(step => processObserver.observe(step));

    // Shop Filters
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;
            productCards.forEach(card => {
                const category = card.dataset.category;
                if (filter === 'all' || category === filter) {
                    card.classList.remove('hidden');
                    card.style.animation = 'fadeInUp 0.5s ease forwards';
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });

    // Product Modal
    /*const modal = document.getElementById('productModal');
    const modalOverlay = modal.querySelector('.modal-overlay');
    const modalClose = modal.querySelector('.modal-close');
    const quickViewBtns = document.querySelectorAll('.quick-view-btn');

    const productData = {
        'Midnight Eclipse': { price: '$289', story: 'Born from the depths of culinary obsession. A masterpiece of dark chocolate layers, infused with midnight espresso and finished with edible charcoal detailing.', materials: 'Belgian Dark Chocolate, Tahitian Vanilla', finishing: 'Matte Black Glaze, Gold Leaf Accents' },
        'Velvet Descent': { price: '$345', story: 'A crimson journey into decadence. Layers of red velvet embrace a core of dark cherry compote, crowned with burgundy mirror glaze.', materials: 'French Butter, Madagascar Vanilla, Dark Cherries', finishing: 'Burgundy Mirror Glaze, Edible Crystals' },
        'Shadow Throne': { price: '$420', story: 'The pinnacle of our obsidian collection. Triple chocolate layers with whiskey ganache, entombed in volcanic ash finish.', materials: 'Valrhona Chocolate, Japanese Whiskey', finishing: 'Volcanic Ash Texture, Platinum Dust' },
        'Abyss Layer': { price: '$275', story: 'Darkness distilled into confection. Charcoal sponge with black sesame cream, kissed by subtle hints of matcha.', materials: 'Activated Charcoal, Black Sesame, Ceremonial Matcha', finishing: 'Silk Matte Black, Abstract Gold Lines' },
        'Crimson Veil': { price: '$310', story: 'Behind the veil lies perfection. Raspberry-infused layers beneath a dramatic red velvet exterior.', materials: 'Fresh Raspberries, European Cream, Red Cocoa', finishing: 'Draped Crimson Fondant, Pearl Accents' },
        'Obsidian Monarch': { price: '$495', story: 'Our crown jewel. A limited edition masterpiece featuring five distinct chocolate layers from around the world.', materials: 'Single-Origin Chocolates from 5 Countries', finishing: 'Crystalline Black Mirror, 24K Gold Crown' }
    };

    quickViewBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const card = btn.closest('.product-card');
            const name = card.querySelector('.product-name').textContent;
            const data = productData[name];

            modal.querySelector('.modal-product-name').textContent = name;
            modal.querySelector('.modal-story p').textContent = data.story;
            modal.querySelector('.price-value').textContent = data.price;
            modal.querySelectorAll('.spec-value')[0].textContent = data.materials;
            modal.querySelectorAll('.spec-value')[1].textContent = data.finishing;

            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    });

    [modalOverlay, modalClose].forEach(el => {
        el.addEventListener('click', () => {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }); */
    const modal = document.getElementById('productModal');

    if (modal) {
        const modalOverlay = modal.querySelector('.modal-overlay');
        const modalClose = modal.querySelector('.modal-close');
        const quickViewBtns = document.querySelectorAll('.quick-view-btn');

        quickViewBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            });
        });

        [modalOverlay, modalClose].forEach(el => {
            el.addEventListener('click', () => {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }


    // Option buttons
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.parentElement.querySelectorAll('.option-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Range buttons
    document.querySelectorAll('.range-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Stats Counter
    const stats = document.querySelectorAll('.stat-number');
    const statsObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.dataset.count);
                let current = 0;
                const increment = target / 50;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        entry.target.textContent = target;
                        clearInterval(timer);
                    } else {
                        entry.target.textContent = Math.floor(current);
                    }
                }, 30);
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    stats.forEach(stat => statsObserver.observe(stat));

    // Form Submission
    /* const customForm = document.getElementById('customForm');
     customForm.addEventListener('submit', e => {
         e.preventDefault();
         const btn = customForm.querySelector('.submit-btn span');
         btn.textContent = 'Request Submitted';
         setTimeout(() => {
             btn.textContent = 'Submit Request';
             customForm.reset();
             document.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active'));
         }, 3000);
     });
 */
    const customForm = document.getElementById('customForm');

    if (customForm) {
        customForm.addEventListener('submit', () => {
            const btn = customForm.querySelector('.submit-btn span');
            btn.textContent = 'Submitting...';
        });
    }

    // Cart functionality
    let cartCount = 0;
    const cartCountEl = document.querySelector('.cart-count');

    document.querySelectorAll('.claim-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            cartCount++;
            cartCountEl.textContent = cartCount;
            cartCountEl.style.animation = 'pulse 0.3s ease';
            setTimeout(() => cartCountEl.style.animation = '', 300);
            modal.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    // Parallax hover effect for cards
    document.querySelectorAll('.parallax-hover').forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `perspective(1000px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg) scale(1.05)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateY(0) rotateX(0) scale(1)';
        });
    });

    // Keyboard navigation for modal
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Active section detection
    const sections = document.querySelectorAll('section[id]');
    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 200;
            if (window.scrollY >= sectionTop) current = section.getAttribute('id');
        });
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) link.classList.add('active');
        });
    });
});

// CSS Animation for filter
const style = document.createElement('style');
style.textContent = `@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }`;
document.head.appendChild(style);
