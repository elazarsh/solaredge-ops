import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Hebrew-capable fonts bundled locally (Google Fonts is not reachable at render time).
// Variable fonts cover the full weight range with a single file.
export const FONTS = {
  heebo: "Heebo",
  rubik: "Rubik",
  assistant: "Assistant",
  fredoka: "Fredoka",
  secular: "Secular One",
  suez: "Suez One",
  karantina: "Karantina",
  varela: "Varela Round",
} as const;

export const fontsLoaded = Promise.all([
  loadFont({ family: FONTS.heebo, url: staticFile("fonts/Heebo-VF.ttf"), weight: "100 900" }),
  loadFont({ family: FONTS.rubik, url: staticFile("fonts/Rubik-VF.ttf"), weight: "300 900" }),
  loadFont({ family: FONTS.assistant, url: staticFile("fonts/Assistant-VF.ttf"), weight: "200 800" }),
  loadFont({ family: FONTS.fredoka, url: staticFile("fonts/Fredoka-VF.ttf"), weight: "300 700" }),
  loadFont({ family: FONTS.secular, url: staticFile("fonts/SecularOne-Regular.ttf") }),
  loadFont({ family: FONTS.suez, url: staticFile("fonts/SuezOne-Regular.ttf") }),
  loadFont({ family: FONTS.karantina, url: staticFile("fonts/Karantina-Bold.ttf"), weight: "700" }),
  loadFont({ family: FONTS.varela, url: staticFile("fonts/VarelaRound-Regular.ttf") }),
]);
