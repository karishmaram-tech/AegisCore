package cmd

import (
	"fmt"
	"os"

	"github.com/karishmaram-tech/AegisCore/clients/launcher/internal/ui"
	"github.com/spf13/cobra"
)

var version = "dev"

var rootCmd = &cobra.Command{
	Use:   "aegiscore",
	Short: "Aegiscore — Autonomous Hacking Agent for Red Team",
	Long:  ui.RenderBanner() + "\n" + ui.Dim.Render("Autonomous Hacking Agent for Red Team"),
	CompletionOptions: cobra.CompletionOptions{
		HiddenDefaultCmd: true,
	},
	SilenceUsage:  true,
	SilenceErrors: true,
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}
}

func init() {
	rootCmd.Version = version
	rootCmd.SetVersionTemplate(fmt.Sprintf("Aegiscore %s\n", version))
}
