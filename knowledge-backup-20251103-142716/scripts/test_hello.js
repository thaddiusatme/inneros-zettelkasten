/**
 * Simple test script to verify Templater user scripts are working
 */
module.exports = async (tp) => {
    console.log('[Test] Hello from user script!');
    new Notice('✅ User scripts are working!');
    return 'Hello World!';
};
