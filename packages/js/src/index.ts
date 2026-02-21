import { createRequire } from "node:module";

import { Command } from "commander";

import { registerCommands } from "./cli.js";

const require = createRequire(import.meta.url);
const { version } = require("../package.json") as { version: string };

const program = new Command();
program
  .name("envoic")
  .description("Discover and manage node_modules and JS artifacts")
  .version(version);

registerCommands(program);
program.parse();
