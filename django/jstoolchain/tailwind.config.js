module.exports = {
  mode: "jit",
  purge: ["../templates/**/*.html"],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      fill: theme => ({

        'red': theme('colors.red.500'),

        'green': theme('colors.green.500'),

        'blue': theme('colors.blue.500'),
      })
    },
  },
  variants: {
    extend: {
      fill: ['hover', 'focus'],

    },
  },
  plugins: [require("@tailwindcss/forms"), require("daisyui")],
};
