import { useEffect, useState, useCallback, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "@/stores/useAuthStore";
import { useSwipeStore } from "@/stores/useSwipeStore";
import { SwipeCard } from "@/components/molecules/SwipeCard";
import { getUserTopicIds } from "@/services/opinionsService";

const SwipePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const urlUserId = searchParams.get("userId");

  // Zustand stores with selective subscriptions (only what we need)
  const userId = useAuthStore((state) => state.userId);
  const getCurrentIdea = useSwipeStore((state) => state.getCurrentIdea);
  const answerIdea = useSwipeStore((state) => state.answerIdea);
  const markMatchShown = useSwipeStore((state) => state.markMatchShown);
  const loadOpinions = useSwipeStore((state) => state.loadOpinions);
  const isLoading = useSwipeStore((state) => state.isLoading);
  const error = useSwipeStore((state) => state.error);

  // Subscribe to actual values instead of functions
  const answers = useSwipeStore((state) => state.answers);
  const hasShownImminentMatch = useSwipeStore((state) => state.hasShownImminentMatch);

  const currentIdea = getCurrentIdea();

  // Calculate shouldShowMatch from values
  const shouldShowMatch = answers.length >= 8 && !hasShownImminentMatch;
  const [hasInitialized, setHasInitialized] = useState(false);
  const [swipeDirection, setSwipeDirection] = useState<"left" | "right" | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Refs for touch/mouse handling
  const cardRef = useRef<HTMLDivElement>(null);
  const startX = useRef(0);
  const currentX = useRef(0);

  // Load opinions when component mounts
  useEffect(() => {
    const initializeOpinions = async () => {
      const effectiveUserId = urlUserId || userId;

      if (!effectiveUserId) {
        setHasInitialized(true);
        return;
      }

      try {
        const topicIds = await getUserTopicIds(effectiveUserId);
        await loadOpinions(topicIds.length > 0 ? topicIds : undefined);
      } catch (err) {
        console.error("Error initializing opinions:", err);
      } finally {
        setHasInitialized(true);
      }
    };

    initializeOpinions();
  }, [urlUserId, userId, loadOpinions]);

  // Check if should show match
  useEffect(() => {
    if (shouldShowMatch) {
      markMatchShown();
      setIsTransitioning(true);
      setTimeout(() => {
        navigate(`/match?userId=${urlUserId || userId}`);
      }, 500);
    }
  }, [shouldShowMatch, markMatchShown, navigate, urlUserId, userId]);

  // Redirect when all ideas answered
  useEffect(() => {
    // Only redirect if we've initialized AND we have ideas loaded but currentIdea is null
    // This means all ideas have been answered
    if (hasInitialized && !currentIdea && !isLoading && answers.length > 0) {
      navigate(`/reveal?userId=${urlUserId || userId}`);
    }
  }, [hasInitialized, currentIdea, isLoading, navigate, urlUserId, userId, answers.length]);

  // Handle swipe with useCallback to prevent recreation
  const handleSwipe = useCallback((direction: "left" | "right") => {
    const effectiveUserId = urlUserId || userId;
    if (!effectiveUserId || !cardRef.current) return;

    const answer = direction === "right" ? "agree" : "disagree";

    // Add exit animation class
    cardRef.current.classList.add(
      direction === "right" ? "animate-swipe-right" : "animate-swipe-left"
    );

    // Wait for animation to complete, then answer
    setTimeout(() => {
      answerIdea(effectiveUserId, answer);

      // Reset card position and remove animation class
      if (cardRef.current) {
        cardRef.current.classList.remove("animate-swipe-right", "animate-swipe-left");
        cardRef.current.style.transform = "";
      }
    }, 300);
  }, [urlUserId, userId, answerIdea]);

  // Touch/Mouse handlers with useCallback
  const handleDragStart = useCallback((clientX: number) => {
    setIsDragging(true);
    startX.current = clientX;
    currentX.current = clientX;
  }, []);

  const handleDragMove = useCallback((clientX: number) => {
    if (!isDragging || !cardRef.current) return;

    currentX.current = clientX;
    const diff = currentX.current - startX.current;

    // Update card position with CSS transform (hardware accelerated)
    const rotation = diff * 0.1; // Subtle rotation based on drag
    const opacity = 1 - Math.abs(diff) / 400;

    cardRef.current.style.transform = `translateX(${diff}px) rotate(${rotation}deg)`;
    cardRef.current.style.opacity = `${Math.max(0.5, opacity)}`;

    // Update direction indicator
    if (Math.abs(diff) > 50) {
      setSwipeDirection(diff > 0 ? "right" : "left");
    } else {
      setSwipeDirection(null);
    }
  }, [isDragging]);

  const handleDragEnd = useCallback(() => {
    if (!isDragging || !cardRef.current) return;

    const diff = currentX.current - startX.current;
    const threshold = 100;
    const velocity = Math.abs(diff);

    if (velocity > threshold) {
      // Complete the swipe
      handleSwipe(diff > 0 ? "right" : "left");
    } else {
      // Snap back with CSS transition
      cardRef.current.style.transition = "transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s ease";
      cardRef.current.style.transform = "";
      cardRef.current.style.opacity = "";

      setTimeout(() => {
        if (cardRef.current) {
          cardRef.current.style.transition = "";
        }
      }, 300);
    }

    setIsDragging(false);
    setSwipeDirection(null);
  }, [isDragging, handleSwipe]);

  // Event listeners
  const onMouseDown = useCallback((e: React.MouseEvent) => {
    handleDragStart(e.clientX);
  }, [handleDragStart]);

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    handleDragMove(e.clientX);
  }, [handleDragMove]);

  const onMouseUp = useCallback(() => {
    handleDragEnd();
  }, [handleDragEnd]);

  const onTouchStart = useCallback((e: React.TouchEvent) => {
    handleDragStart(e.touches[0].clientX);
  }, [handleDragStart]);

  const onTouchMove = useCallback((e: React.TouchEvent) => {
    handleDragMove(e.touches[0].clientX);
  }, [handleDragMove]);

  const onTouchEnd = useCallback(() => {
    handleDragEnd();
  }, [handleDragEnd]);

  // Loading state
  if (isLoading) {
    return (
      <div className="h-screen w-full fixed inset-0 liquid-background flex items-center justify-center">
        <div className="text-white text-xl">Cargando opiniones...</div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="h-screen w-full fixed inset-0 liquid-background flex items-center justify-center px-4">
        <div className="text-white text-center">
          <div className="text-xl mb-4">Error</div>
          <div className="text-sm opacity-80">{error}</div>
        </div>
      </div>
    );
  }

  // No current idea
  if (!currentIdea) {
    return null;
  }

  return (
    <div className={`h-screen w-full fixed inset-0 overflow-hidden liquid-background animate-fade-in ${isTransitioning ? 'animate-slide-up-exit' : ''}`}>
      <div className="h-full w-full flex items-center justify-center px-4 sm:px-6">
        <div
          ref={cardRef}
          className="w-full max-w-lg cursor-grab active:cursor-grabbing gpu-accelerated select-none"
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={onMouseUp}
          onTouchStart={onTouchStart}
          onTouchMove={onTouchMove}
          onTouchEnd={onTouchEnd}
        >
          <SwipeCard
            idea={currentIdea}
            swipeDirection={swipeDirection}
          />
        </div>
      </div>
    </div>
  );
};

export default SwipePage;
