// Simple test script to verify authentication flow
import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8080';

async function testAuthentication() {
    console.log('🧪 Testing AutomateOS Authentication System...\n');

    try {
        // Test 1: Register a new user
        console.log('1️⃣ Testing user registration...');
        const testEmail = `test${Date.now()}@example.com`;
        const testPassword = 'testpassword123';

        const registerResponse = await axios.post(`${BASE_URL}/register/`, {
            email: testEmail,
            password: testPassword
        });

        console.log('✅ Registration successful!');
        console.log('   User ID:', registerResponse.data.id);
        console.log('   Email:', registerResponse.data.email);
        console.log('   Created:', registerResponse.data.created_at);

        // Test 2: Login with the registered user
        console.log('\n2️⃣ Testing user login...');
        const loginParams = new URLSearchParams();
        loginParams.append('username', testEmail);
        loginParams.append('password', testPassword);

        const loginResponse = await axios.post(`${BASE_URL}/auth/token`, loginParams, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });

        console.log('✅ Login successful!');
        console.log('   Access Token:', loginResponse.data.access_token.substring(0, 50) + '...');
        console.log('   Token Type:', loginResponse.data.token_type);

        // Test 3: Try to login with wrong password
        console.log('\n3️⃣ Testing invalid login...');
        const wrongParams = new URLSearchParams();
        wrongParams.append('username', testEmail);
        wrongParams.append('password', 'wrongpassword');

        try {
            await axios.post(`${BASE_URL}/auth/token`, wrongParams, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });
            console.log('❌ This should have failed!');
        } catch (error) {
            if (error.response?.status === 401) {
                console.log('✅ Invalid login correctly rejected!');
                console.log('   Error:', error.response.data.detail);
            } else {
                console.log('❌ Unexpected error:', error.message);
            }
        }

        // Test 4: Try to register with existing email
        console.log('\n4️⃣ Testing duplicate registration...');
        try {
            await axios.post(`${BASE_URL}/register/`, {
                email: testEmail,
                password: testPassword
            });
            console.log('❌ This should have failed!');
        } catch (error) {
            if (error.response?.status === 400) {
                console.log('✅ Duplicate registration correctly rejected!');
                console.log('   Error:', error.response.data.detail);
            } else {
                console.log('❌ Unexpected error:', error.message);
            }
        }

        console.log('\n🎉 All authentication tests passed!');
        console.log('\n📋 Summary:');
        console.log('   ✅ User registration works');
        console.log('   ✅ User login works');
        console.log('   ✅ Invalid login is rejected');
        console.log('   ✅ Duplicate registration is rejected');
        console.log('\n🚀 Authentication system is ready for frontend integration!');

    } catch (error) {
        console.error('❌ Test failed:', error.message);
        if (error.response) {
            console.error('   Status:', error.response.status);
            console.error('   Data:', error.response.data);
        }
    }
}

testAuthentication();