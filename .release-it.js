module.exports = {
    hooks: {
        'before:init': 'git fetch --prune --prune-tags origin'
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