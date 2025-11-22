import { useState, useEffect, useCallback, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { useTopicsStore } from "@/stores/useTopicsStore";
import { useSwipeStore } from "@/stores/useSwipeStore";

interface Topic {
  id: number;
  name: string;
  emoji: string;
}

const TopicsPage = () => {
  const { topics: storeTopics, setTopics } = useTopicsStore();
  const resetSwipe = useSwipeStore((state) => state.resetSwipe);

  const [topics, setLocalTopics] = useState<Topic[]>(storeTopics);
  const [selectedTopics, setSelectedTopics] = useState<number[]>([]);
  const [loading, setLoading] = useState(storeTopics.length === 0);
  const [submitting, setSubmitting] = useState(false);
  const [showTitle, setShowTitle] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const navigate = useNavigate();
  const { toast } = useToast();

  // Convert selectedTopics array to Set for O(1) lookup
  const selectedTopicsSet = useMemo(() => new Set(selectedTopics), [selectedTopics]);

  useEffect(() => {
    fetchTopics();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowTitle(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const fetchTopics = async () => {
    try {
      const { data, error } = await supabase
        .from("Topics")
        .select("id, name, emoji")
        .order("name");

      if (error) throw error;

      const topicsData = data || [];
      setLocalTopics(topicsData);
      setTopics(topicsData);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "No se pudieron cargar los temas",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Use useCallback to prevent function recreation on every render
  const toggleTopic = useCallback((topicId: number) => {
    setSelectedTopics(prev => {
      if (prev.includes(topicId)) {
        return prev.filter(id => id !== topicId);
      } else if (prev.length < 5) {
        return [...prev, topicId];
      }
      return prev;
    });
  }, []);

  const handleSubmit = useCallback(async () => {
    if (selectedTopics.length === 0) {
      toast({
        title: "Selecciona al menos un tema",
        description: "Debes elegir entre 1 y 5 temas",
        variant: "destructive",
      });
      return;
    }

    setSubmitting(true);

    try {
      const { data: { session } } = await supabase.auth.getSession();

      let userId: string;

      if (session?.user) {
        userId = session.user.id;
      } else {
        const { data: authData, error: authError } = await supabase.auth.signInAnonymously();

        if (authError) throw authError;
        if (!authData.user?.id) throw new Error("No se pudo crear el usuario");

        userId = authData.user.id;
      }

      // Prepare user topics (memoized in useCallback deps)
      const userTopics = selectedTopics.map(topicId => ({
        user_id: userId,
        topic_id: topicId,
      }));

      const { error } = await supabase
        .from("UserTopics")
        .insert(userTopics);

      if (error) throw error;

      setIsTransitioning(true);

      setTimeout(() => {
        navigate(`/swipe?userId=${userId}`);
      }, 600);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "No se pudieron guardar tus preferencias",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  }, [selectedTopics, toast, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center gradient-subtle">
        <p className="text-lg text-muted-foreground">Cargando temas...</p>
      </div>
    );
  }

  return (
    <div className={`min-h-screen liquid-background p-6 transition-all-smooth ${isTransitioning ? 'animate-fade-out-up' : ''}`}>
      {showTitle ? (
        <div
          key="title"
          className="min-h-screen flex items-start justify-center pt-20 animate-fade-in"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-foreground text-center">
            Elige tus temas de interés
          </h2>
        </div>
      ) : (
        <div className="animate-fade-in">
          <div className="max-w-2xl mx-auto py-12 pb-32">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {topics.map((topic, index) => {
                const isSelected = selectedTopicsSet.has(topic.id);

                return (
                  <div
                    key={topic.id}
                    className={`
                      stagger-item relative aspect-square rounded-2xl shadow-card
                      cursor-pointer flex flex-col items-center justify-center gap-3 p-4
                      glass-effect hover-lift transition-all-smooth
                      ${isSelected ? 'border-2 border-primary scale-105' : 'border border-border/50'}
                    `}
                    onClick={() => toggleTopic(topic.id)}
                    style={{ animationDelay: `${index * 0.05}s` }}
                  >
                    {isSelected && (
                      <div className="absolute top-3 right-3 w-6 h-6 rounded-full bg-primary flex items-center justify-center animate-scale-in">
                        <svg className="w-4 h-4 text-primary-foreground" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                    <div
                      className={`text-5xl md:text-6xl transition-transform-smooth ${isSelected ? 'scale-110' : ''}`}
                    >
                      {topic.emoji || '📌'}
                    </div>
                    <p className="font-semibold text-foreground text-sm md:text-base text-center">
                      {topic.name}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Floating button */}
      {!showTitle && (
        <div className="fixed bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-background via-background to-transparent pointer-events-none animate-fade-in-up">
          <div className="max-w-2xl mx-auto pointer-events-auto">
            <Button
              onClick={handleSubmit}
              size="lg"
              className="w-full text-lg py-6 shadow-elevated"
              disabled={submitting || selectedTopics.length === 0}
            >
              {submitting ? "Guardando..." : "Comenzar a conocer candidatos"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TopicsPage;
