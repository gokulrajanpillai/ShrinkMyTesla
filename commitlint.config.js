export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat', // new feature
        'fix', // bug fix
        'chore', // maintenance / tooling
        'docs', // documentation changes
        'refactor', // code changes that aren’t bug fixes or features
        'style', // formatting only (no code change)
        'build', // build system or external dependency changes
        'ci', // continuous integration related changes
      ],
    ],
    'subject-case': [
      2,
      'never',
      ['sentence-case', 'start-case', 'pascal-case', 'upper-case'],
    ],
  },
}
