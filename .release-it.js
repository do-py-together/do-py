module.exports = {
    hooks: {
        'before:init': 'git fetch --prune --prune-tags origin',
        'after:release': 'yarn clean && yarn build && pipenv run twine upload dist/* && yarn clean'
    },
    git: {
        tagName: 'v${version}',
        commitMessage: 'Release: v${version}',
        tagAnnotation: 'Release:',
        requireCleanWorkingDir: true,
        requireBranch: 'master',
        requireUpstream: true,
        requireCommits: true
    },
    npm: {
        publish: false
    }
}