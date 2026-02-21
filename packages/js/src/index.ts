import { Command } from "commander";

import { registerCommands } from "./cli.js";

const program = new Command();
program
  .name("envoic")
  .description("Discover and manage node_modules and JS artifacts")
  .version("0.1.0");

registerCommands(program);
program.parse();
