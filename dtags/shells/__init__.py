from dtags.shells import bash, zsh, fish

SUPPORTED_SHELLS = {
    'zsh': zsh.CONFIGURATION,
    'bash': bash.D_COMMAND,
    'fish': fish.CONFIGURATION,
}
