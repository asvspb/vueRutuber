module.exports = {
  customSyntax: 'postcss-html',
  extends: [
    'stylelint-config-standard-scss',
    'stylelint-config-recommended-vue'
  ],
  plugins: [
    'stylelint-order'
  ],
  rules: {
    // BEM naming with allowances for `u-*` utilities and `is-*` states
    // block, block__element, block--modifier, block__element--modifier
    // kebab-case with digits allowed
    'selector-class-pattern': [
      // Allow:
      // - Utilities: u-*
      // - States: is-*
      // - Existing project utilities: btn, container, responsive-title, shadow-1..5, gradient-primary|success|warning
      // - BEM: block, block__element, block--modifier, block__element--modifier
      '^(?:'
        + '(?:u-[a-z0-9-]+)'
        + '|(?:is-[a-z0-9-]+)'
        + '|(?:btn(?:--[a-z0-9-]+)?)'
        + '|(?:container)'
        + '|(?:responsive-title)'
        + '|(?:shadow-[1-5])'
        + '|(?:gradient-(?:primary|success|warning))'
        + '|(?:[a-z0-9]+(?:-[a-z0-9]+)*(?:__(?:[a-z0-9]+(?:-[a-z0-9]+)*))?(?:--[a-z0-9]+(?:-[a-z0-9]+)*)?)'
      + ')$',
      {
        resolveNestedSelectors: true,
        message: 'Class names must follow BEM (block__element--modifier) or allowed prefixes (u-, is-) or project utility allowlist.'
      }
    ],

    // Keep selectors simple
    'selector-max-compound-selectors': 4,

    // SCSS nesting depth
    'max-nesting-depth': 4,

    // Property ordering for readability
    'order/properties-alphabetical-order': null,

    // General recommendations
    'color-hex-length': 'short',
    'property-no-vendor-prefix': null,
    'no-duplicate-selectors': true,

    // SCSS compatibility and formatting leniency for SFCs
    'at-rule-no-unknown': null,
    'scss/at-rule-no-unknown': true,
    'declaration-empty-line-before': null,
    'at-rule-empty-line-before': null,
    'declaration-property-value-no-unknown': null,
  },
  ignoreFiles: [
    'dist/**/*',
    'node_modules/**/*',
    'coverage/**/*',
    'playwright-report/**/*',
    'docs/**/*'
  ]
}
