import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(ROOT, relative), 'utf8'));

test('root owner descriptor is a portable regular copy of the canonical capability manifest', () => {
  const descriptorPath = path.join(ROOT, 'opl-package.json');
  const manifestPath = path.join(ROOT, 'contracts/opl_capability_package_manifest.json');
  const packageManifest = readJson('contracts/opl_capability_package_manifest.json');

  assert.equal(fs.lstatSync(descriptorPath).isSymbolicLink(), false);
  assert.equal(fs.lstatSync(descriptorPath).isFile(), true);
  assert.deepEqual(fs.readFileSync(descriptorPath), fs.readFileSync(manifestPath));
  assert.deepEqual(readJson('opl-package.json'), packageManifest);
  assert.equal(packageManifest.package_role, 'capability_package');
  assert.equal(packageManifest.capability_abi.id, 'mas-scholar-skills.v1');
  const expectedConfiguredCarrier = {
    kind: 'codex_plugin_manager',
    plugin_selector: 'mas-scholar-skills@mas-scholar-skills',
    marketplace_source: 'gaofeng21cn/mas-scholar-skills',
    publication_ref: 'ghcr.io/gaofeng21cn/one-person-lab-packages/mas-scholar-skills:latest-stable',
    executor_route: 'codex_cli',
  };
  assert.deepEqual(packageManifest.codex_surface, {
    plugin_id: 'mas-scholar-skills',
    carrier_source_role: 'codex_plugin_carrier_not_package_truth',
    consumer_profiles_ref: '#/consumer_profiles',
    default_materialized_skill_ids_ref: '#/exports/all_skill_ids',
    codex_default_exposure: false,
    optional_install_policy: 'all_exported_skills',
    configured_codex_plugin_carrier: expectedConfiguredCarrier,
  });
  for (const key of Object.keys(expectedConfiguredCarrier)) {
    assert.equal(Object.hasOwn(packageManifest, key), false, `${key} must stay under codex_surface`);
  }
  assert.equal(Object.hasOwn(packageManifest, 'configured_codex_plugin_carrier'), false);
  assert.equal(Object.hasOwn(packageManifest, 'managed_update_source'), false);
});

test('Agent Plugins root carrier and Codex carrier share the canonical interface', () => {
  const agentPlugin = readJson('plugin.json');
  const codexPlugin = readJson('.codex-plugin/plugin.json');
  assert.equal(agentPlugin.name, codexPlugin.name);
  assert.equal(agentPlugin.version, codexPlugin.version);
  assert.deepEqual(agentPlugin.extensions?.['com.openai']?.interface, codexPlugin.interface);
  assert.equal(Object.hasOwn(agentPlugin, 'skills'), false);
  assert.equal(codexPlugin.skills, './skills/');
});

test('repo marketplace exposes the repository root as the single plugin source', () => {
  const marketplace = readJson('.agents/plugins/marketplace.json');
  const plugin = readJson('.codex-plugin/plugin.json');
  const [entry] = marketplace.plugins;

  assert.equal(marketplace.name, 'mas-scholar-skills');
  assert.equal(marketplace.interface.displayName, 'MAS Scholar Skills');
  assert.equal(marketplace.plugins.length, 1);
  assert.equal(entry.name, plugin.name);
  assert.deepEqual(entry.source, { source: 'local', path: './' });
  assert.deepEqual(entry.policy, {
    installation: 'AVAILABLE',
    authentication: 'ON_INSTALL',
  });
  assert.equal(entry.category, plugin.interface.category);
  assert.equal(plugin.skills, './skills/');
  assert.equal(fs.existsSync(path.join(ROOT, 'plugins', plugin.name)), false);
});

test('Codex plugin carries exactly the package-owned active Skill sources', () => {
  const plugin = readJson('.codex-plugin/plugin.json');
  const packageManifest = readJson('contracts/opl_capability_package_manifest.json');
  const expected = [...packageManifest.exports.all_skill_ids].sort();
  const actual = fs.readdirSync(path.join(ROOT, 'skills'), { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .filter((entry) => fs.existsSync(path.join(ROOT, 'skills', entry.name, 'SKILL.md')))
    .map((entry) => entry.name)
    .sort();

  assert.equal(plugin.name, packageManifest.package_id);
  assert.equal(plugin.version, packageManifest.version);
  assert.deepEqual(actual, expected);
  assert.equal(actual.length, 36);
  for (const skillId of actual) {
    const skillPath = path.join(ROOT, 'skills', skillId, 'SKILL.md');
    assert.equal(fs.lstatSync(skillPath).isSymbolicLink(), false, `${skillId} must be a real source file`);
  }
});

test('retired metadata stays outside Codex Skill discovery', () => {
  const contract = readJson('contracts/scholar-skills-capability-modules.json');
  const retired = contract.codex_skill_exposure_policy.optional_redirect_tombstone_skill_ids;

  assert.equal(retired.length, 4);
  for (const skillId of retired) {
    assert.equal(fs.existsSync(path.join(ROOT, 'skills', skillId)), false);
    assert.equal(
      fs.existsSync(path.join(ROOT, 'tombstones', 'skills', skillId, 'TOMBSTONE.md')),
      true,
    );
  }
});
