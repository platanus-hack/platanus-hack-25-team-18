import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useTopicsStore } from "@/stores/useTopicsStore";
import { supabase } from "@/integrations/supabase/client";

const LandingPage = () => {
  const navigate = useNavigate();
  const setTopics = useTopicsStore((state) => state.setTopics);

  useEffect(() => {
    // Precargar temas
    const loadTopics = async () => {
      try {
        const { data, error } = await supabase
          .from("Topics")
          .select("id, name, emoji")
          .order("name");

        if (!error && data) {
          setTopics(data);
        }
      } catch (error) {
        console.error("Error precargando temas:", error);
      }
    };

    loadTopics();
  }, [setTopics]);

  const handleStart = () => {
    navigate("/topics");
  };

  return (
    <div className="h-[100dvh] w-screen flex flex-col items-center justify-center overflow-hidden fixed inset-0 liquid-background animate-fade-in">
      {/* Contenido central */}
      <div className="flex flex-col items-center justify-center relative z-10 gap-8 px-6">
        {/* Título */}
        <div className="text-center animate-fade-in-up">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 drop-shadow-2xl">
            MiCandidatop
          </h1>
          <p className="text-xl md:text-2xl text-white/90 font-medium drop-shadow-lg">
            Encuentra tu match político
          </p>
        </div>

        {/* Botón principal */}
        <Button
          onClick={handleStart}
          size="lg"
          className="text-xl px-12 py-8 shadow-glow hover:scale-105 transition-transform animate-scale-in"
          style={{ animationDelay: '0.2s' }}
        >
          Descubre tu candidato
        </Button>
      </div>
    </div>
  );
};

export default LandingPage;
