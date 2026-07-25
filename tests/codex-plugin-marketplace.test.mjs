import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(ROOT, relative), 'utf8'));

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
  assert.equal(actual.length, 35);
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
