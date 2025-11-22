import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAppContext } from "@/context/AppContext";
import { getTopCandidate } from "@/data/mockData";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { motion } from "framer-motion";
import { fadeInUp, scaleIn, spring, createStaggerContainer } from "@/config/animations";
import confetti from "canvas-confetti";

interface Topic {
  id: number;
  name: string;
  emoji: string;
}

const MatchPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const userId = searchParams.get("userId");
  const { answers, candidates } = useAppContext();
  const { toast } = useToast();

  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);

  const topCandidate = getTopCandidate(answers, candidates);

  useEffect(() => {
    fetchTopics();

    // Trigger confetti on mount
    const timer = setTimeout(() => {
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#ff0080', '#7c3aed', '#06b6d4', '#f59e0b'],
      });

      // Secondary burst
      setTimeout(() => {
        confetti({
          particleCount: 50,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: ['#ff0080', '#7c3aed'],
        });
        confetti({
          particleCount: 50,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: ['#06b6d4', '#f59e0b'],
        });
      }, 200);
    }, 600);

    return () => clearTimeout(timer);
  }, []);

  const fetchTopics = async () => {
    try {
      const { data, error } = await supabase
        .from("Topics")
        .select("id, name, emoji")
        .order("name");

      if (error) throw error;
      setTopics(data || []);
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

  if (!topCandidate) {
    navigate(`/?userId=${userId}`);
    return null;
  }

  if (loading) {
    return (
      <div className="h-screen w-full flex items-center justify-center liquid-background">
        <p className="text-lg text-muted-foreground">Cargando...</p>
      </div>
    );
  }

  return (
    <motion.div
      className="h-screen w-full fixed inset-0 overflow-hidden liquid-background"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={spring.smooth}
    >
      <div className="h-full w-full overflow-y-auto">
        {/* Sección Superior - Avatar con Blur */}
        <div className="flex flex-col items-center justify-center pt-16 pb-8 px-6 mt-24">
          {/* Avatar con blur y burbuja de chat */}
          <div className="flex items-center gap-4 mb-6">
            <motion.div
              className="relative"
              variants={scaleIn}
              initial="hidden"
              animate="visible"
              transition={{ ...spring.bouncy, delay: 0.2 }}
            >
              <img
                src={topCandidate.avatarUrl}
                alt="Match"
                className="w-40 h-40 rounded-full blur-avatar shadow-elevated"
              />
              <div className="absolute inset-0 rounded-full bg-gradient-primary/10" />
            </motion.div>

            <motion.div
              className="flex flex-col gap-2"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ ...spring.smooth, delay: 0.4 }}
            >
              {/* Burbuja de texto */}
              <motion.div
                className="relative py-3 px-5 rounded-2xl bg-card border border-border text-foreground font-medium shadow-card"
                initial={{ scale: 0, originX: 0 }}
                animate={{ scale: 1 }}
                transition={{ ...spring.bouncy, delay: 0.5 }}
              >
                Conozcámonos
                {/* Triángulo de la burbuja */}
                <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-2 w-0 h-0 border-t-8 border-t-transparent border-b-8 border-b-transparent border-r-8 border-r-card"></div>
              </motion.div>

              {/* Botón de chat */}
              <motion.button
                onClick={() => navigate(`/chat?userId=${userId}`)}
                className="py-1.5 px-2 rounded-lg gradient-primary text-primary-foreground shadow-elevated hover:shadow-glow self-end text-lg"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ ...spring.bouncy, delay: 0.6 }}
                whileHover={{ scale: 1.1, rotate: 5 }}
                whileTap={{ scale: 0.9 }}
              >
                💬
              </motion.button>
            </motion.div>
          </div>
        </div>

        {/* Sección Inferior - Cards de Temas */}
        <motion.div
          className="px-6 pb-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          <motion.div
            className="max-w-2xl mx-auto"
            variants={createStaggerContainer(0.05, 0.8)}
            initial="hidden"
            animate="visible"
          >
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {topics.map((topic) => (
                <motion.div
                  key={topic.id}
                  variants={fadeInUp}
                  className="relative aspect-square bg-card rounded-2xl shadow-card cursor-pointer flex flex-col items-center justify-center gap-3 p-4 border border-border/50 glass-effect"
                  onClick={() => navigate(`/topic-swipe?userId=${userId}&topicId=${topic.id}&candidateId=${topCandidate.id}`)}
                  whileHover={{ y: -4, scale: 1.03, boxShadow: "0 20px 25px -5px rgb(0 0 0 / 0.15)" }}
                  whileTap={{ scale: 0.98 }}
                  transition={spring.smooth}
                >
                  <div className="text-5xl md:text-6xl">
                    {topic.emoji || '📌'}
                  </div>
                  <p className="font-semibold text-foreground text-sm md:text-base text-center">
                    {topic.name}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default MatchPage;
