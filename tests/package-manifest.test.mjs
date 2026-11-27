import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(ROOT, relative), 'utf8'));

test('v2 package exports its complete active Skill and module catalog', () => {
  const manifest = readJson('opl-package.json');
  const domainContract = readJson('contracts/opl_capability_package_manifest.json');
  const skills = manifest.provides.skills;
  const expectedSkillIds = domainContract.exports.all_skill_ids;
  const actualSkillIds = skills.map((skill) => skill.id);
  const actualModuleIds = manifest.provides.module_ids;

  assert.equal(manifest.schema_version, 'opl.package.v2');
  assert.equal(manifest.identity.id, 'mas-scholar-skills');
  assert.equal(manifest.identity.version, '0.2.33');
  assert.equal(manifest.identity.intent, 'extension');
  assert.equal(manifest.identity.publisher, 'one-person-lab');
  assert.equal(manifest.identity.license, 'Apache-2.0');
  assert.equal(manifest.identity.repository, 'https://github.com/gaofeng21cn/mas-scholar-skills');
  assert.deepEqual(actualSkillIds, expectedSkillIds);
  assert.equal(skills.length, 36);
  assert.deepEqual(skills.filter((skill) => skill.exposure === 'default').map((skill) => skill.id), [
    'mas-scholar-skills',
  ]);

  const activeSkillDirectories = fs.readdirSync(path.join(ROOT, 'skills'), { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .filter((entry) => fs.existsSync(path.join(ROOT, 'skills', entry.name, 'SKILL.md')))
    .map((entry) => entry.name)
    .sort();
  assert.deepEqual([...actualSkillIds].sort(), activeSkillDirectories);
  for (const skill of skills) {
    assert.equal(skill.path, `./skills/${skill.id}`);
    assert.equal(skill.exposure, skill.id === 'mas-scholar-skills' ? 'default' : 'opt_in');
    assert.ok(fs.lstatSync(path.join(ROOT, skill.path, 'SKILL.md')).isFile());
  }

  assert.deepEqual(actualModuleIds, domainContract.exports.core_module_ids);
  assert.equal(actualModuleIds.length, 10);
  assert.deepEqual(manifest.dependencies, {
    opl_base: '^2.0.0',
    runtimes: [{ name: 'python', version: '>=3.12' }],
  });
  assert.deepEqual(manifest.distribution, {
    oci: 'ghcr.io/gaofeng21cn/one-person-lab-packages/mas-scholar-skills',
    visibility: 'public',
  });
  assert.deepEqual(manifest.host_hints.codex, {
    sync_enabled: false,
    plugin_name: 'mas-scholar-skills',
    category: 'Research',
  });
});

test('tombstones stay outside the v2 Skill discovery catalog', () => {
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
