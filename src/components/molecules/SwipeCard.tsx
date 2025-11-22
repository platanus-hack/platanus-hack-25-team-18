import { memo } from "react";
import { Idea } from "@/data/mockData";
import { TopicTag } from "@/components/atoms/TopicTag";
import { cn } from "@/lib/utils";
import { Heart, X } from "lucide-react";

interface SwipeCardProps {
  idea: Idea;
  className?: string;
  swipeDirection?: "left" | "right" | null;
}

// Memoized component to prevent unnecessary re-renders
export const SwipeCard = memo(({ idea, className, swipeDirection }: SwipeCardProps) => {
  return (
    <div className="relative w-full max-w-lg mx-auto">
      {/* Swipe indicators with CSS animations */}
      <div
        className={cn(
          "absolute -left-24 top-1/2 -translate-y-1/2 transition-all-smooth",
          swipeDirection === "left" ? "opacity-100 scale-110" : "opacity-0 scale-75"
        )}
      >
        <div className="w-20 h-20 rounded-full bg-destructive/20 backdrop-blur-xl border-2 border-destructive flex items-center justify-center">
          <div className={swipeDirection === "left" ? "animate-pulse" : ""}>
            <X className="w-10 h-10 text-destructive" strokeWidth={3} />
          </div>
        </div>
      </div>

      <div
        className={cn(
          "absolute -right-24 top-1/2 -translate-y-1/2 transition-all-smooth",
          swipeDirection === "right" ? "opacity-100 scale-110" : "opacity-0 scale-75"
        )}
      >
        <div className="w-20 h-20 rounded-full bg-success/20 backdrop-blur-xl border-2 border-success flex items-center justify-center">
          <div className={swipeDirection === "right" ? "animate-pulse" : ""}>
            <Heart className="w-10 h-10 text-success" strokeWidth={3} fill="currentColor" />
          </div>
        </div>
      </div>

      {/* Main card with liquid glass effect and CSS animations */}
      <div
        className={cn(
          "relative w-full animate-scale-in",
          "glass-effect",
          "rounded-[3rem] p-8 md:p-12",
          "h-[600px] flex flex-col items-center justify-center",
          "gpu-accelerated",
          className
        )}
      >
        {/* Topic tag */}
        <div className="mb-8 animate-fade-in-down" style={{ animationDelay: '0.1s' }}>
          <TopicTag topic={idea.topicName} />
        </div>

        {/* Emoji/Icon with bounce */}
        {idea.emoji && (
          <div className="text-7xl mb-8 text-center drop-shadow-2xl animate-scale-in" style={{ animationDelay: '0.2s' }}>
            {idea.emoji}
          </div>
        )}

        {/* Idea text */}
        <p className="text-xl font-semibold text-foreground leading-relaxed text-center mb-12 px-4 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          {idea.text}
        </p>

        {/* Swipe hint */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
          <div className="flex items-center gap-4 text-muted-foreground/60">
            <div className="flex items-center gap-2">
              <X className="w-5 h-5" />
              <span className="text-sm font-medium">Desliza</span>
            </div>
            <div className="w-12 h-1 rounded-full bg-muted-foreground/20" />
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Desliza</span>
              <Heart className="w-5 h-5" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function for memo
  // Only re-render if idea.id or swipeDirection changes
  return prevProps.idea.id === nextProps.idea.id &&
         prevProps.swipeDirection === nextProps.swipeDirection;
});

SwipeCard.displayName = 'SwipeCard';
