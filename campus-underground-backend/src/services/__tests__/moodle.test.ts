import { MoodleAPIClient } from '../moodle';
import axios from 'axios';
import { mocked } from 'jest-mock';

jest.mock('axios');

const mockedAxios = mocked(axios);

describe('MoodleAPIClient', () => {
  let client: MoodleAPIClient;
  const mockConfig = {
    url: 'https://moodle.concordia.ca',
    token: 'test-token'
  };

  beforeEach(() => {
    client = new MoodleAPIClient(mockConfig);
    mockedAxios.get.mockClear();
  });

  describe('getCourses', () => {
    it('should fetch user courses successfully', async () => {
      const mockResponse = {
        data: {
          data: [
            {
              id: 1,
              fullname: 'Test Course',
              shortname: 'TC101'
            }
          ]
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {
          url: 'https://moodle.concordia.ca/webservice/rest/server.php',
          params: {
            wstoken: 'test-token',
            wsfunction: 'core_enrol_get_users_courses',
            moodlewsrestformat: 'json',
            userid: 123
          }
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await client.getCourses(123);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        'https://moodle.concordia.ca/webservice/rest/server.php',
        {
          params: {
            wstoken: 'test-token',
            wsfunction: 'core_enrol_get_users_courses',
            moodlewsrestformat: 'json',
            userid: 123
          }
        }
      );
      expect(result).toEqual(mockResponse.data.data);
    });

    it('should throw error when API returns error', async () => {
      const mockErrorResponse = {
        data: {
          error: 'Invalid token'
        },
        status: 400,
        statusText: 'Bad Request',
        headers: {},
        config: {
          url: 'https://moodle.concordia.ca/webservice/rest/server.php',
          params: {
            wstoken: 'test-token',
            wsfunction: 'core_enrol_get_users_courses',
            moodlewsrestformat: 'json',
            userid: 123
          }
        }
      };

      mockedAxios.get.mockResolvedValue(mockErrorResponse);

      await expect(client.getCourses(123)).rejects.toThrow('Moodle API Error: Invalid token');
    });

    it('should throw error when request fails', async () => {
      const error = new Error('Network error');
      mockedAxios.get.mockRejectedValue(error);

      await expect(client.getCourses(123)).rejects.toThrow('Moodle API Error: Network error');
    });
  });

  describe('getCourseContents', () => {
    it('should fetch course contents successfully', async () => {
      const mockResponse = {
        data: {
          data: [
            {
              id: 1,
              name: 'Week 1',
              contents: []
            }
          ]
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {
          url: 'https://moodle.concordia.ca/webservice/rest/server.php',
          params: {
            wstoken: 'test-token',
            wsfunction: 'core_course_get_contents',
            moodlewsrestformat: 'json',
            courseid: 101
          }
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await client.getCourseContents(101);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        'https://moodle.concordia.ca/webservice/rest/server.php',
        {
          params: {
            wstoken: 'test-token',
            wsfunction: 'core_course_get_contents',
            moodlewsrestformat: 'json',
            courseid: 101
          }
        }
      );
      expect(result).toEqual(mockResponse.data.data);
    });
  });
});
