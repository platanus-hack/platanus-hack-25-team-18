import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAppContext } from "@/context/AppContext";
import { SwipeCard } from "@/components/molecules/SwipeCard";
import { getUserTopicIds } from "@/services/opinionsService";
import { motion, useMotionValue, useTransform, PanInfo } from "framer-motion";
import { spring, swipeConfig } from "@/config/animations";

const SwipePage = () => {
  console.log("SwipePage component mounted");

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const userId = searchParams.get("userId");

  console.log("SwipePage - userId from URL:", userId);
  console.log("SwipePage - searchParams:", searchParams.toString());

  const {
    getCurrentIdea,
    answerIdea,
    shouldShowMatch,
    markMatchShown,
    loadOpinions,
    isLoading,
    error,
    userId: contextUserId,
  } = useAppContext();

  const currentIdea = getCurrentIdea();
  const [hasInitialized, setHasInitialized] = useState(false);
  const [swipeDirection, setSwipeDirection] = useState<"left" | "right" | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Framer Motion values for smooth dragging
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 0, 200], [-swipeConfig.rotation, 0, swipeConfig.rotation]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0.5, 1, 1, 1, 0.5]);

  console.log("SwipePage - contextUserId:", contextUserId);

  // Load opinions when component mounts
  useEffect(() => {
    console.log("SwipePage - useEffect triggered");

    const initializeOpinions = async () => {
      // Use userId from URL if available, otherwise use context userId
      const effectiveUserId = userId || contextUserId;

      console.log("SwipePage - effectiveUserId:", effectiveUserId);

      if (!effectiveUserId) {
        console.log("SwipePage - No userId found, skipping initialization");
        setHasInitialized(true);
        return;
      }

      try {
        // Get user's selected topics
        const topicIds = await getUserTopicIds(effectiveUserId);
        console.log("SwipePage - User topics:", topicIds);

        // Load opinions filtered by those topics
        await loadOpinions(topicIds.length > 0 ? topicIds : undefined);
        console.log("SwipePage - Opinions loaded successfully");
      } catch (err) {
        console.error("Error initializing opinions:", err);
      } finally {
        setHasInitialized(true);
      }
    };

    initializeOpinions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId, contextUserId]);

  useEffect(() => {
    if (shouldShowMatch()) {
      markMatchShown();
      // Iniciar animación de transición
      setIsTransitioning(true);
      // Navegar después de la animación
      setTimeout(() => {
        navigate(`/match?userId=${userId}`);
      }, 500);
    }
  }, [shouldShowMatch, markMatchShown, navigate, userId]);

  useEffect(() => {
    // Only redirect if we have initialized and we're not loading and there's no current idea
    // This prevents redirecting before opinions are loaded
    if (hasInitialized && !currentIdea && !isLoading) {
      // All ideas answered, go to reveal
      navigate(`/reveal?userId=${userId}`);
    }
  }, [hasInitialized, currentIdea, isLoading, navigate, userId]);

  // Update swipe direction indicator based on drag position
  useEffect(() => {
    const unsubscribe = x.on("change", (latest) => {
      if (Math.abs(latest) > 50) {
        setSwipeDirection(latest > 0 ? "right" : "left");
      } else {
        setSwipeDirection(null);
      }
    });

    return () => unsubscribe();
  }, [x]);


  console.log("SwipePage render - isLoading:", isLoading, "currentIdea:", currentIdea, "hasInitialized:", hasInitialized);

  // Show loading state
  if (isLoading) {
    return (
      <div className="h-screen w-full fixed inset-0 liquid-background flex items-center justify-center">
        <div className="text-white text-xl">Cargando opiniones...</div>
      </div>
    );
  }

  // Show error state
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

  const handleDragEnd = (_event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const { offset, velocity } = info;

    // Check if velocity is high enough for a flick
    const isFlick = Math.abs(velocity.x) > swipeConfig.velocityThreshold;
    // Check if distance is far enough
    const isSwipe = Math.abs(offset.x) > swipeConfig.threshold;

    if (isFlick || isSwipe) {
      // Complete the swipe
      if (offset.x > 0) {
        answerIdea("agree");
      } else {
        answerIdea("disagree");
      }
      // Animate card out of view
      x.set(offset.x > 0 ? 500 : -500);
    } else {
      // Snap back with spring physics
      x.set(0);
    }

    // Reset direction indicator
    setSwipeDirection(null);
  };

  // Render conditions AFTER all hooks
  if (!currentIdea) {
    console.log("SwipePage - No current idea, returning null");
    return null;
  }

  return (
    <motion.div
      className="h-screen w-full fixed inset-0 overflow-hidden liquid-background"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={spring.smooth}
    >
      <div className={`h-full w-full flex items-center justify-center px-4 sm:px-6 ${isTransitioning ? 'animate-slide-up-exit' : ''}`}>
        <motion.div
          className="w-full max-w-lg cursor-grab active:cursor-grabbing"
          style={{
            x,
            rotate,
            opacity,
          }}
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={0.7}
          onDragEnd={handleDragEnd}
          transition={swipeConfig.transition}
          whileTap={{ cursor: "grabbing" }}
        >
          <SwipeCard
            idea={currentIdea}
            swipeDirection={swipeDirection}
          />
        </motion.div>
      </div>
    </motion.div>
  );
};

export default SwipePage;
