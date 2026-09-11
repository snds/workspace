import type { ComponentBlueprint } from "../types";

export const avatarBlueprint: ComponentBlueprint = {
  id: "avatar",
  name: "Avatar",
  category: "display",
  description: "A circular avatar displaying initials or an image",
  icon: "display/avatar",
  tags: ["avatar", "profile", "user", "image", "initials"],

  props: [
    { name: "initials", type: "string", label: "Initials", defaultValue: "AB", affectsCanvas: true },
    { name: "src", type: "string", label: "Image URL" },
    { name: "alt", type: "string", label: "Alt Text", defaultValue: "Avatar" },
    {
      name: "size", type: "enum", label: "Size", defaultValue: "default",
      options: [
        { value: "sm", label: "Small" },
        { value: "default", label: "Default" },
        { value: "lg", label: "Large" },
      ],
    },
  ],

  tokenBindings: {
    background: "avatar.background",
    foreground: "avatar.foreground",
  },

  canvasTemplate: {
    type: "frame",
    width: 40,
    height: 40,
    fill: "avatar.background",
    cornerRadius: 9999,
    children: [
      {
        name: "Initials", type: "text",
        offsetX: 0, offsetY: 0, width: 40, height: 40,
        text: "AB", textColor: "avatar.foreground",
        fontSize: 14, fontWeight: 500, textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/avatar",
      componentName: "Avatar",
      propMappings: { src: "src", alt: "alt" },
      additionalImports: ["AvatarImage", "AvatarFallback"],
      wrapper: "<Avatar><AvatarImage /><AvatarFallback>{initials}</AvatarFallback></Avatar>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Avatar",
      componentName: "Avatar",
      propMappings: { src: "src", alt: "alt", initials: "children" },
    },
  },
};
