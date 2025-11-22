import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import HoldButton from "@/components/atoms/HoldButton";
import { useAppContext } from "@/context/AppContext";
import { supabase } from "@/integrations/supabase/client";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { spring } from "@/config/animations";

const LandingPage = () => {
  const navigate = useNavigate();
  const { setTopics } = useAppContext();
  const [blurAmount, setBlurAmount] = useState(20);

  // Motion values for smooth animations
  const progress = useMotionValue(0);
  const blur = useTransform(progress, [0, 100], [20, 0]);
  const scale = useTransform(progress, [0, 100], [1.1, 1]);

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

  const handleHoldProgress = (progressValue: number) => {
    // Update motion value for smooth animation
    progress.set(progressValue);
    // Keep state for backward compatibility
    const newBlur = 20 - (progressValue / 100) * 20;
    setBlurAmount(newBlur);
  };

  const handleHoldComplete = () => {
    setBlurAmount(0);
    setTimeout(() => {
      navigate("/topics");
    }, 800);
  };

  return (
    <motion.div
      className="h-[100dvh] w-screen flex items-center justify-center overflow-hidden fixed inset-0"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={spring.smooth}
    >
      {/* Fondo con imagen de chile con blur */}
      <motion.div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat will-change-transform"
        style={{
          backgroundImage: "url('/screen/chile.png')",
          filter: blur,
          scale: scale,
        }}
      />

      {/* Contenido */}
      <motion.div
        className="flex items-center justify-center relative z-10"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ ...spring.bouncy, delay: 0.2 }}
      >
        <HoldButton
          onComplete={handleHoldComplete}
          onProgressChange={handleHoldProgress}
        />
      </motion.div>
    </motion.div>
  );
};

export default LandingPage;
