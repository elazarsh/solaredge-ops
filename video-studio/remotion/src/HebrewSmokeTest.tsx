import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FONTS } from "./fonts";

// Toolchain check: RTL Hebrew text, local fonts, spring motion, color cut on the beat.
const WORDS = ["מעון", "מלא", "באהבה"];
const COLORS = ["#FF5A5F", "#FFB400", "#00A699"];

export const HebrewSmokeTest: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const beat = Math.floor(frame / (fps * 0.8)) % COLORS.length;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS[beat],
        direction: "rtl",
        justifyContent: "center",
        alignItems: "center",
        gap: 20,
        flexDirection: "column",
      }}
    >
      {WORDS.map((word, i) => {
        const p = spring({ frame: frame - i * 8, fps, config: { damping: 12 } });
        return (
          <div
            key={word}
            style={{
              fontFamily: FONTS.heebo,
              fontWeight: 900,
              fontSize: 220,
              lineHeight: 1,
              color: "white",
              transform: `translateY(${interpolate(p, [0, 1], [200, 0])}px) scale(${p})`,
              opacity: p,
            }}
          >
            {word}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
