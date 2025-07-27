const axios = require('axios');
const { Configuration, OpenAIApi } = require('openai');
const db = require('../models'); // Assuming you have a database models setup
const moodleService = require('./moodleService');
const fs = require('fs');
const path = require('path');

// Load .env file manually
const envPath = path.resolve(__dirname, '../.env');
console.log('Attempting to load .env file from:', envPath);

let openaiApiKey = process.env.OPENAI_API_KEY;

// If API key is not in environment, try to load it directly from .env file
if (!openaiApiKey) {
  try {
    const envContent = fs.readFileSync(envPath, 'utf8');
    const match = envContent.match(/OPENAI_API_KEY=(.+)/);
    if (match && match[1]) {
      openaiApiKey = match[1].trim();
      console.log('Loaded OpenAI API key directly from .env file');
    }
  } catch (error) {
    console.error('Error loading .env file:', error);
  }
}

// Debug logging for environment variables
console.log('OpenAI API key status:');
console.log('OPENAI_API_KEY exists:', !!openaiApiKey);
console.log('OPENAI_API_KEY first 5 chars:', openaiApiKey ? openaiApiKey.substring(0, 5) : 'undefined');

// Configure OpenAI
const configuration = new Configuration({
  apiKey: openaiApiKey,
});
const openai = new OpenAIApi(configuration);

class GPTFlashcardService {
  /**
   * Generate flashcards from course notes
   * @param {number} courseId - Moodle course ID
   * @param {string} userId - User ID
   * @returns {Promise<Array>} - Array of generated flashcards
   */
  async generateFlashcardsFromCourse(courseId, userId) {
    try {
      // 1. Get course content from Moodle
      const courseContent = await moodleService.getCourseContent(courseId, userId);
      
      // 2. Extract text content from course materials
      const textContent = this.extractTextFromCourseContent(courseContent);
      
      if (!textContent || textContent.length === 0) {
        throw new Error('No content found to generate flashcards from');
      }
      
      // 3. Generate flashcards using GPT
      const flashcards = await this.generateFlashcardsWithGPT(textContent, courseId, userId);
      
      // 4. Store generated flashcards in the flashcard database
      await this.storeFlashcards(flashcards, courseId, userId);
      
      return flashcards;
    } catch (error) {
      console.error('Error generating flashcards:', error);
      throw error;
    }
  }
  
  /**
   * Extract text content from course materials
   * @param {Object} courseContent - Course content from Moodle
   * @returns {string} - Extracted text
   */
  extractTextFromCourseContent(courseContent) {
    // Logic to extract text from various content types
    // This would handle PDFs, HTML, plain text, etc.
    let extractedText = '';
    
    // Example implementation - would need to be expanded based on content types
    if (courseContent.modules) {
      courseContent.modules.forEach(module => {
        if (module.description) {
          extractedText += module.description + '\n\n';
        }
        
        if (module.contents) {
          module.contents.forEach(content => {
            if (content.type === 'file' && content.mimetype === 'text/plain') {
              // For text files, you'd need to fetch and extract content
              extractedText += content.content || '';
            }
          });
        }
      });
    }
    
    return extractedText;
  }
  
  /**
   * Generate flashcards using GPT API
   * @param {string} content - Text content to generate flashcards from
   * @param {number} courseId - Course ID
   * @param {string} userId - User ID
   * @returns {Promise<Array>} - Array of generated flashcards
   */
  async generateFlashcardsWithGPT(content, courseId, userId) {
    try {
      // Split content into chunks if it's too large
      const chunks = this.splitContentIntoChunks(content, 4000);
      let allFlashcards = [];
      
      for (const chunk of chunks) {
        const prompt = `
          Generate 5 high-quality flashcards from the following educational content.
          For each flashcard, create a question and answer pair.
          Format the output as a JSON array of objects with 'question' and 'answer' properties.
          Make the questions challenging but clear, and the answers concise but complete.
          
          Content:
          ${chunk}
        `;
        
        console.log('Sending request to OpenAI API with model:', 'gpt-3.5-turbo');
        try {
          const response = await openai.createChatCompletion({
            model: "gpt-3.5-turbo",
            messages: [
              {
                role: "system",
                content: "You are a helpful assistant that generates educational flashcards."
              },
              {
                role: "user",
                content: prompt
              }
            ],
            max_tokens: 1000,
            temperature: 0.7,
          });
          
          console.log('OpenAI API response status:', response.status);
          console.log('OpenAI API response headers:', JSON.stringify(response.headers));
          
          const responseText = response.data.choices[0].message.content.trim();
          console.log('GPT API response text:', responseText);
          
          try {
            // Clean up the response text if it's wrapped in markdown code blocks
            let cleanedText = responseText;
            
            // Remove markdown code block syntax if present
            const codeBlockMatch = cleanedText.match(/```(?:json)?\s*([\s\S]+?)\s*```/);
            if (codeBlockMatch && codeBlockMatch[1]) {
              cleanedText = codeBlockMatch[1].trim();
            }
            
            console.log('Cleaned JSON text:', cleanedText);
            
            // Parse the JSON response
            const flashcards = JSON.parse(cleanedText);
            allFlashcards = [...allFlashcards, ...flashcards];
          } catch (parseError) {
            console.error('Error parsing GPT response:', parseError);
            console.error('Raw response text:', responseText);
            // Fallback parsing logic could be implemented here
          }
        } catch (apiError) {
          console.error('OpenAI API error:', apiError.message);
          if (apiError.response) {
            console.error('Error status:', apiError.response.status);
            console.error('Error data:', JSON.stringify(apiError.response.data));
          }
          throw new Error(`OpenAI API error: ${apiError.message}`);
        }
      }
      
      // Add metadata to each flashcard
      return allFlashcards.map(card => ({
        ...card,
        course_id: courseId,
        user_id: userId,
        created_at: new Date(),
        review_count: 0,
        difficulty: 'medium',
      }));
    } catch (error) {
      console.error('Error calling GPT API:', error);
      throw error;
    }
  }
  
  /**
   * Split content into smaller chunks for API processing
   * @param {string} content - Content to split
   * @param {number} maxLength - Maximum chunk length
   * @returns {Array<string>} - Array of content chunks
   */
  splitContentIntoChunks(content, maxLength) {
    const chunks = [];
    let currentChunk = '';
    
    // Split by paragraphs first
    const paragraphs = content.split('\n\n');
    
    for (const paragraph of paragraphs) {
      if (currentChunk.length + paragraph.length < maxLength) {
        currentChunk += paragraph + '\n\n';
      } else {
        chunks.push(currentChunk);
        currentChunk = paragraph + '\n\n';
      }
    }
    
    if (currentChunk) {
      chunks.push(currentChunk);
    }
    
    return chunks;
  }
  
  /**
   * Store generated flashcards in the database
   * @param {Array} flashcards - Generated flashcards
   * @param {number} courseId - Course ID
   * @param {string} userId - User ID
   * @returns {Promise<void>}
   */
  async storeFlashcards(flashcards, courseId, userId) {
    try {
      // Create a deck for these flashcards
      const deck = await db.FlashcardDeck.create({
        title: `Generated Flashcards - Course ${courseId}`,
        description: 'Automatically generated from course content',
        subject: 'Course Materials',
        course_id: courseId,
        user_id: userId,
        created_at: new Date(),
        updated_at: new Date(),
      });
      
      // Create all flashcards in the deck
      const flashcardPromises = flashcards.map(card => 
        db.Flashcard.create({
          deck_id: deck.id,
          question: card.question,
          answer: card.answer,
          difficulty: card.difficulty,
          review_count: 0,
          created_at: new Date(),
          updated_at: new Date(),
          user_id: userId,
        })
      );
      
      await Promise.all(flashcardPromises);
      
      return deck;
    } catch (error) {
      console.error('Error storing flashcards:', error);
      throw error;
    }
  }
  
  /**
   * Process user feedback to improve flashcard generation
   * @param {string} flashcardId - ID of the flashcard
   * @param {string} feedback - User feedback
   * @returns {Promise<void>}
   */
  async processUserFeedback(flashcardId, feedback) {
    // Store feedback for future training
    await db.FlashcardFeedback.create({
      flashcard_id: flashcardId,
      feedback: feedback,
      created_at: new Date()
    });
    
    // This feedback could be used to fine-tune the GPT model
    // or adjust generation parameters in the future
  }
}

module.exports = new GPTFlashcardService();
