import "./index.css";
import { Composition } from "remotion";
import { fontsLoaded } from "./fonts";
import { HebrewSmokeTest } from "./HebrewSmokeTest";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HebrewSmokeTest"
        component={HebrewSmokeTest}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={async () => {
          await fontsLoaded;
          return {};
        }}
      />
    </>
  );
};
