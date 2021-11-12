module.exports = {
    extends: ["eslint:recommended"],
    rules: {
        indent: ["error", 4],
        quotes: ["error", "double", { avoidEscape: true, allowTemplateLiterals: true }],
        "no-multiple-empty-lines": ["error", { max: 2, maxEOF: 0 }],
        "quote-props": ["error", "as-needed"],
        "brace-style": ["error", "1tbs", { allowSingleLine: true }],
    },
    env: {
        browser: true,
        jquery: true,
        node: true
    },
    globals: {
        d3: true
    },
    parserOptions: {
        sourceType: "module",
        ecmaVersion: 2015
    }
};