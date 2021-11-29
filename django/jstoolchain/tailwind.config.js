
const plugin = require("tailwindcss/plugin");

// const siblingCheckedPlugin = plugin(function ({ addVariant, e }) {
//   addVariant("sibling-checked", ({ container }) => {
//     container.walkRules((rule) => {
//       rule.selector = `:checked + .sibling-checked\\:${rule.selector.slice(1)}`;
//     });
//   });
// });

module.exports = {
  mode: "jit",
  purge: ["../templates/**/*.html"],
  darkMode: 'class', // or 'media' or 'class'
  theme: {
    extend: {
      fill: theme => ({
        'red': theme('colors.red.500'),
        'green': theme('colors.green.500'),
        'yellow': theme('colors.yellow.300'),
        'dark-yellow': theme('colors.yellow.500'),
        'gray': theme('colors.green.300'),
        'blue': theme('colors.blue.500'),
      }),
      colors: {
        site: '#FF6E0A'
      }
    },
  },
  variants: {
    extend: {

      fill: ['hover', 'focus']

    },
  },
  plugins: [require("@tailwindcss/forms"), require("daisyui")],
};
